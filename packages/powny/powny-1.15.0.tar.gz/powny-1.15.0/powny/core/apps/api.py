import logging

import flask
import flask_api.app

import gunicorn.app.base
import gunicorn.glogging

from contextlog import get_logger

from .. import backends
from .. import tools
from .. import api
from .. import backdoor

from ..api.rules import ExposedRulesResource
from ..api.rules import RulesHeadResource

from ..api.jobs import JobsResource
from ..api.jobs import JobControlResource

from ..api.system import StateResource
from ..api.system import InfoResource
from ..api.system import ConfigResource

from ..api.golem import GolemResource

from . import init


# =====
class _Api(flask_api.app.FlaskAPI):
    """
        Versioned REST API.
    """

    def __init__(self, *args, **kwargs):  # pylint: disable=super-init-not-called
        # Yes, __init__ not from a base class
        flask.Flask.__init__(self, *args, **kwargs)  # pylint: disable=non-parent-init-called
        self.api_settings = flask_api.app.APISettings(self.config)
        self.jinja_env.filters["urlize_quoted_links"] = flask_api.app.urlize_quoted_links
        self.register_blueprint(flask.Blueprint(
            name="flask-api",
            import_name="flask_api.app",
            url_prefix="/flask-api",
            static_folder="static",
        ))
        self.register_blueprint(flask.Blueprint(
            name="powny-api",
            import_name="powny.core.api",
            template_folder="templates",
        ))
        self._resources = {}
        self.add_url_rule("/", "API's list", self._get_apis)

    def add_url_resource(self, version, url_rule, resource):
        def handler(**kwargs):
            return resource.handler(**kwargs)
        handler.__doc__ = resource.docstring
        self.add_url_rule(
            url_rule,
            resource.name,
            handler,
            methods=resource.methods
        )
        self._resources.setdefault(version, [])
        self._resources[version].append(resource)

    def _get_apis(self):
        """ View available API's """
        return {
            version: [
                {"name": resource.name, "url": api.get_url_for(resource)}
                for resource in resources
                if not resource.dynamic
            ]
            for (version, resources) in self._resources.items()
        }


# =====
def make_app(config):
    """
        Use this functions without arguments to create UWSGI app.
    """

    if config.backdoor.enabled:
        backdoor.start(config.backdoor.port)

    pool = backends.Pool(
        size=config.api.backend_connections,
        backend_name=config.core.backend,
        backend_opts=config.backend,
    )

    loader = tools.make_loader(config.core.rules_dir)

    app = _Api(__name__)
    app.add_url_resource("v1", "/v1/rules/exposed", ExposedRulesResource(
        pool=pool,
        loader=loader,
    ))
    app.add_url_resource("v1", "/v1/rules/head", RulesHeadResource(pool))
    app.add_url_resource("v1", "/v1/jobs", JobsResource(
        pool=pool,
        loader=loader,
        input_limit=config.api.input_limit,
    ))
    app.add_url_resource("v1", "/v1/jobs/<job_id>", JobControlResource(pool, config.api.delete_timeout))
    app.add_url_resource("v1", "/v1/system/state", StateResource(pool))
    app.add_url_resource("v1", "/v1/system/info", InfoResource(pool))
    app.add_url_resource("v1", "/v1/system/config", ConfigResource(config))
    app.add_url_resource("compat", "/api/compat/golem/submit", GolemResource(
        pool=pool,
        loader=loader,
        input_limit=config.api.input_limit,
    ))

    return app


def run(args=None, config=None):
    get_logger(app="api")  # App-level context
    if config is None:
        config = init(__name__, "Powny HTTP API", args)
    _Unicorn(config).run()


# =====
class _Unicorn(gunicorn.app.base.BaseApplication):
    def __init__(self, config):
        self._config = config
        super().__init__()

    def init(self, parser, opts, args):
        pass  # Makes pylint happy

    def load_config(self):
        for (option, value) in self._config.api.gunicorn.items():
            self.cfg.set(option, value)
        self.cfg.set("logger_class", _UnicornLogger)
        self.cfg.set("accesslog", "-")  # For working accesslog (see gunicorn/glogging.py:270)

    def load(self):
        app = make_app(self._config)
        get_logger().critical("Ready to work on %s", self.cfg.bind)
        return app


class _UnicornLogger(gunicorn.glogging.Logger):
    def __init__(self, cfg):  # pylint: disable=super-init-not-called
        self.error_log = logging.getLogger("gunicorn.error")
        self.access_log = logging.getLogger("gunicorn.access")
        self.cfg = cfg

    def setup(self, _):
        pass  # Don't configure logging using the gunicorn options
