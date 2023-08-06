import concurrent.futures
import functools
from time import time as now
import sys
import time
from timeit import timeit

import ujson as json
from flask import request, Response

import hancock


def signed(key_func, log_func=sys.stdout.write, expire_seconds=10):
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
    def signed_decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # Get the public key
            key = request.args.get("apikey")
            if not key:
                return '', 401
            # Get the private key for the public key.
            p_key = key_func(key)
            if not p_key:
                log_func("No private key for: {key}".format(key=key))
                return '', 401

            # Validate the request.
            method = request.method
            query = dict(request.args)
            status_code, message = hancock.validate(p_key, query, expire_seconds, method)
            if status_code != 200:
                log_func(message)
                return '', status_code

            # Invoke the handler
            return fn(*args, **kwargs)

        return wrapper
    return signed_decorator


def status(jobs):
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
    def status_handler():
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
        for job, future in [(job, executor.submit(timeit, job[2], number=1)) for job in jobs]:
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

        json_data = json.dumps(stats)
        resp = Response(response=json_data,
                status=200,
                mimetype="application/json")
        executor.shutdown(wait=False)
        return resp
        # TODO: Look into potentially cleaning up jobs that have timed-out.
        #
        #       This could be done by changing jobs from a func to an object
        #       that implements `def interrupt(self):` which would be used
        #       to interrupt/stop/close/cleanup any resources.
    return status_handler


def ping():
    """Handler that simply returns `pong` from a GET.
    """
    return "pong"


def time():
    """Handler that returns the systems current Epoch time.
    """
    utcnow = now()
    return str(int(utcnow))


def keys(key_store):
    def keys_decorator(fn):
        @wraps(fn)
        def handler(*args, **kwargs):
            key_store.load_keys()
        return handler
    return keys_decorator

def private_keys(key_store):
    def private_keys_decorator(fn):
        @wraps(fn)
        def handler(*args, **kwargs):
            key_store.load_private_key()
        return handler
    return private_keys_decorator

def authorized_keys(key_store):
    def authorized_keys_decorator(fn):
        @wraps(fn)
        def handler(*args, **kwargs):
            if request.method == "GET":
                keys = key_store.keys()
                return json.dumps(keys)
            elif request.method == "PUT":
                key_store.load_keys()
        return handler
    return authorized_keys_decorator
