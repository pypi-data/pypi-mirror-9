import json, sys, time
from os import environ

from flask import Flask

import tinflask.handlers


class Application(object):
    """tinflask.web.Application instance.

    The built-in `/status` endpoint now requires authorization.
    Keys endpoints are also added to hot-reload authorized/private keys, and
    simple listing of loaded public keys.

    A new instance will set the global key function within tinflask.handlers for
    all signed/authorized endpoints. This key function retrieves private keys
    for the authorization process.
    """

    def __init__(self, handlers=None, **settings):
        """Creates a new tinflask/app with the given handlers and settings.

        - If an `ENDPOINT` environment variable is set all handlers will be prefixed with it.
        - The `status` endpoint is re-added as a signed endpoint.
        - Key endpoints `keys`, `keys/private`, and `keys/authorized` are also added as signed endpoints.
        """

        # Composite app.
        self.app = Flask(__name__)

        # Set the port, defaulting to 8000
        try:
            port_str = environ.get("PORT", "8080")
            self.port = int(port_str)
        except ValueError:
            self.port = 8080

        # Set the host and endpoint
        self.debug = True if environ.get("DEBUG") == "true" else False
        self.address = environ.get("HOST", "0.0.0.0")
        self.jobs = []

        # Add standard endpoints.
        self.app.route("/ping")(tinflask.handlers.ping)
        self.app.route("/time")(tinflask.handlers.time)
        status_handler = tinflask.handlers.status(self.jobs)
        self.app.route("/status")(status_handler)

    def add_status_job(self, name, timeout, job_func):
        """Adds the given status job to the collection of jobs.
        """
        self.jobs.append((name, timeout, job_func,))

    def run(self):
        """Starts the Flask service using the address, port, and debug values
        found from either environment variables or config variables.
        """
        self.app.run(host=self.address, port=self.port, debug=self.debug)
