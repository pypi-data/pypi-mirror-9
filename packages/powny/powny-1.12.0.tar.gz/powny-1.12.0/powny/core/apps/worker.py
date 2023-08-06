import sys
import os
import signal
import multiprocessing
import threading
import errno
import uuid
import logging
import time

from contextlog import get_logger

from .. import context
from .. import backends

from . import init
from . import Application


# =====
_stop = None


def run(args=None, config=None):
    if config is None:
        config = init(__name__, "Powny Worker", args)
    app = _Worker(config)
    global _stop
    _stop = app.stop
    return abs(app.run())


# =====
class _Worker(Application):
    def __init__(self, config):
        Application.__init__(self, "worker", config)
        self._pool = None

    def begin(self):
        self._pool = backends.Pool(
            size=self._app_config.backend_connections,
            backend_name=self._config.core.backend,
            backend_opts=self._config.backend,
        )

    def process(self):
        logger = get_logger()
        sleep_mode = False
        with self.get_backend_object().connected() as backend:
            manager = _JobsManager(self._config.core.rules_dir, backend, self._pool)
            gen_jobs = None
            while not self._stop_event.is_set():
                if gen_jobs is None:
                    gen_jobs = backend.jobs_process.get_jobs()
                manager.manage()
                self._dump_worker_state(manager, backend)
                if self._get_free_slots(manager):
                    try:
                        job = next(gen_jobs)
                    except StopIteration:
                        if not sleep_mode:
                            logger.debug("No jobs, sleeping for %(delay)f seconds...",
                                         {"delay": self._app_config.empty_sleep})
                        sleep_mode = True
                        gen_jobs = None
                        time.sleep(self._app_config.empty_sleep)
                    else:
                        sleep_mode = False
                        manager.run_job(job)
                        time.sleep(self._app_config.job_delay)
                else:
                    logger.debug("Reached the max of concurrent jobs %(maxjobs)d, sleeping for %(delay)f seconds...",
                                 {"maxjobs": self._app_config.max_jobs, "delay": self._app_config.max_jobs_sleep})
                    time.sleep(self._app_config.max_jobs_sleep)

    def _get_free_slots(self, manager):
        return max(self._app_config.max_jobs - manager.get_current(), 0)

    def _dump_worker_state(self, manager, backend):
        self.dump_app_state(backend, {
            "active": manager.get_current(),
            "processed": manager.get_finished(),
            "not_started": manager.get_failed(),  # FIXME: Remove this
            "finished": manager.get_finished(),
            "failed": manager.get_failed(),
        })


class _JobsManager:
    def __init__(self, rules_dir_path, holder_backend, pool):
        self._rules_dir_path = rules_dir_path
        self._holder_backend = holder_backend
        self._pool = pool
        self._controllers = {}
        self._finished = 0
        self._failed = 0

    def get_finished(self):
        return self._finished

    def get_failed(self):
        return self._failed

    def get_current(self):
        return len(self._controllers)

    def run_job(self, job):
        try:
            self._inner_run_job(job)
        except Exception:
            self._release(job.job_id)
            raise

    def _inner_run_job(self, job):
        logger = get_logger(job_id=job.job_id, method=job.method_name)

        logger.debug("Creating the job controller...")
        controller = _JobControllerThread(job, self._rules_dir_path, self._holder_backend, self._pool)
        self._controllers[job.job_id] = (job.method_name, controller)

        logger.info("Starting the job controller...")
        controller.start()

    def manage(self):
        for (job_id, (method_name, controller)) in self._controllers.copy().items():
            logger = get_logger(job_id=job_id, method=method_name)

            if not controller.is_alive():
                logger.info("Finished job process %(pid)d with retcode %(retcode)d",
                            {"pid": controller.get_pid(), "retcode": controller.get_retcode()})
                self._release(job_id)
                self._finish(job_id, controller.get_retcode())

            elif self._holder_backend.jobs_process.is_deleted_job(job_id):
                logger.info("Killing job process %(pid)d...", {"pid": controller.get_pid()})
                controller.kill()
                self._release(job_id)
                self._finish(job_id, controller.get_retcode())

    def _release(self, job_id):
        self._holder_backend.jobs_process.release_job(job_id)

    def _finish(self, job_id, retcode):
        self._controllers.pop(job_id)
        if retcode == 0:
            self._finished += 1
        else:
            self._failed += 1


class _JobControllerThread(threading.Thread):
    def __init__(self, job, rules_dir_path, holder_backend, pool):
        threading.Thread.__init__(self, name="JobControllerThread::" + job.job_id)
        self.daemon = True
        self._job = job
        self._holder_backend = holder_backend
        self._pool = pool
        self._proc = _JobProcess(job, rules_dir_path)

    def kill(self):
        self._proc.kill()

    def get_pid(self):
        return self._proc.pid

    def get_retcode(self):
        return self._proc.exitcode

    # ===

    def run(self):
        logger = get_logger(job_id=self._job.job_id, method=self._job.method_name)
        logger.debug("Starting the job process")
        self._proc.start()

        try:
            request = self._proc.get_request(5)  # TODO: Configurable?
            if request is None:
                logger.error("No ping from process, killing...")
                return
            if request["name"] != "ping":
                logger.error("Invalid first IPC request (not PING), killing...")
                return
            self._proc.send_response(request, True)

            while self._proc.is_alive() and self._holder_backend.is_alive():
                request = self._proc.get_request(1)  # TODO: Configurable?
                if request is not None:
                    self._process_request(request)
        except Exception:
            logger.exception("Unhandled controller exception, killing...")
        finally:
            self._proc.kill()

    def _process_request(self, request):
        name = request["name"]
        assert name in ("save_job_state", "done_job"), "Invalid request '{}'".format(name)
        try:
            backends.retry(
                pool=self._pool,
                method=self._process_backend_request,
                args=(request,),
            )
        except Exception:
            self._proc.send_response(request, False)
            raise
        else:
            self._proc.send_response(request, True)

    def _process_backend_request(self, backend, request):
        method = getattr(backend.jobs_process, request["name"])
        method(*request["args"], **request["kwargs"])


class _JobProcess(multiprocessing.Process):
    def __init__(self, job, rules_dir_path):
        multiprocessing.Process.__init__(self, name="JobProcess::" + job.job_id)
        self.daemon = True

        self._job = job
        self._rules_dir_path = rules_dir_path

        (self._conn_ext, self._conn_int) = multiprocessing.Pipe()

        class _Stub:
            pass
        self._dummy_backend = _Stub()
        self._dummy_backend.jobs_process = _Stub()
        self._dummy_backend.jobs_process.save_job_state = self._backend_save_job_state
        self._dummy_backend.jobs_process.done_job = self._backend_done_job

    def get_request(self, timeout):
        if self._conn_ext.poll(timeout):
            return self._conn_ext.recv()
        return None

    def send_response(self, for_request, ok):
        self._conn_ext.send({
            "request_id": for_request["request_id"],
            "ok": ok,
        })

    def kill(self):
        try:
            os.kill(self.pid, signal.SIGKILL)
            self.join()
            return True
        except OSError as err:
            if err.errno == errno.ESRCH:
                return False
            raise

    # ===

    def run(self):
        self._unlock_logging()
        logger = get_logger(job_id=self._job.job_id, method=self._job.method_name)

        head_dir_path = os.path.join(self._rules_dir_path, self._job.head)
        sys.path.insert(0, head_dir_path)
        logger.debug("Prepended '%(head_dir)s' to sys.path", {"head_dir": head_dir_path})

        thread = context.JobThread(
            backend=self._dummy_backend,
            job_id=self._job.job_id,
            state=self._job.state,
            extra={"head": self._job.head},
        )
        thread.daemon = True

        logger.debug("Ping...")
        self._ping()
        logger.debug("...Pong")

        logger.debug("Starting the job thread...")
        thread.start()

        logger.debug("Joining the job thread...")
        thread.join()
        logger.debug("Joined the job thread")

    def _unlock_logging(self):
        # XXX: ULTIMATE EPIC-SIZED CRUTCH!!!111
        # http://bugs.python.org/issue6721
        if logging._lock:  # pylint: disable=protected-access
            logging._lock = threading.RLock()  # pylint: disable=protected-access
        for wr in logging._handlerList:  # pylint: disable=protected-access
            handler = wr()
            if handler and handler.lock:
                handler.lock = threading.RLock()

    # ===

    def _ping(self):
        self._do_request("ping")

    def _backend_save_job_state(self, *args, **kwargs):
        self._do_request("save_job_state", *args, **kwargs)

    def _backend_done_job(self, *args, **kwargs):
        self._do_request("done_job", *args, **kwargs)

    def _do_request(self, name, *args, **kwargs):
        request_id = str(uuid.uuid4())
        logger = get_logger()
        log_attrs = {
            "request_id": request_id,
            "name": name,
        }

        logger.debug("Sending request %(request_id)s/%(name)s...", log_attrs)
        self._conn_int.send({
            "request_id": request_id,
            "name": name,
            "args": args,
            "kwargs": kwargs,
        })
        logger.debug("Sent request %(request_id)s/%(name)s", log_attrs)

        if not self._conn_int.poll(5):  # TODO: Configurable?
            raise RuntimeError("No response from backend")

        logger.debug("Receiving response for %(request_id)s/%(name)s...", log_attrs)
        response = self._conn_int.recv()
        if response["request_id"] != request_id:
            raise RuntimeError("Invalid request_id='{}'".format(request_id))

        if not response["ok"]:
            raise RuntimeError("Failed (not OK) request_id='{}'".format(request_id))
