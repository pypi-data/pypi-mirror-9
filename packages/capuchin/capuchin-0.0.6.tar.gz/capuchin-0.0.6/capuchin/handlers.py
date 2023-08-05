import concurrent.futures
import functools
import json
import time
import sys
import time
from timeit import timeit

from tornado.web import RequestHandler
import hancock


def signed(key_func, log_func=print, expire_seconds=10):
    """Validates the signature of the request before invoking the handler.
    Logging is passed by default to stdout.
    If the signature fails a 401 response is sent.
    If the signature has expired a 406 response is sent.

    key_func       - A function that takes a public key as a single argument and
                     returns the matching private key.
    log_func       - A function taking a single argument to be logged.
    expire_seconds - Integer of how many seconds before authorization is no
                     longer valid.
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            handler = args[0]
            # Get the public key
            key = handler.get_query_argument("apikey")
            if not key:
                handler.set_status(401)
                return
            # Get the private key for the public key.
            p_key = key_func(key)
            if not p_key:
                handler.set_status(401)
                log_func("No private key for:", key)
                return

            # Validate the request.
            r = handler.request
            status_code, message = hancock.validate(p_key, r.query_arguments, expire_seconds, r.method)
            handler.set_status(status_code)
            if status_code != 200:
                log_func(message)
                return

            # Invoke the handler
            fn(*args, **kwargs)

        return wrapper
    return decorator


class StatusHandler(RequestHandler):
    """Handler that calls each status job in a worker pool, attempting to timeout.
    The resulting durations/errors are written to the response
    as JSON.

    eg.

    `{
        "endpoints": [
            { "endpoint": "Jenny's Database", "duration": 1.002556324005127 },
            { "endpoint": "Hotmail", "duration": -1, "error": "route to host down" },
        ]
     }`
    """

    def initialize(self, jobs_func):
        self._jobs = jobs_func

    def get(self):
        endpoints = []
        stats = { "endpoints": None }

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        # This is basically calling the below within the executor:
        #
        #     >>> timeit(job[2], number=1)
        #
        # job is a tuple of (name, timeout, func) so the above is really:
        #     >>> timeit(func, number=1)
        #
        for job, future in [(job, executor.submit(timeit, job[2], number=1)) for job in self._jobs()]:
            name, timeout, _ = job
            endpoint = {"endpoint": name}
            try:
                data = future.result(timeout=timeout)
                endpoint["duration"] = data
            except concurrent.futures.TimeoutError:
                endpoint["error"] = "timeout exceeded"
            except Exception as ex:
                endpoint["error"] = str(ex)
            endpoints.append(endpoint)

        if len(endpoints) > 0:
            stats["endpoints"] = endpoints

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(stats))
        executor.shutdown(wait=False)
        # TODO: Look into potentially cleaning up jobs that have timed-out.
        #
        #       This could be done by changing jobs from a func to an object
        #       that implements `def interrupt(self):` which would be used
        #       to interrupt/stop/close/cleanup any resources.


class PingHandler(RequestHandler):
    """Handler that simply returns `pong` from a GET.
    """

    def get(self):
        self.write("pong")


class TimeHandler(RequestHandler):
    """Handler that returns the systems current Epoch time.
    """

    def get(self):
        utcnow = time.time()
        now_string = str(int(time.time()))
        self.write(now_string)
