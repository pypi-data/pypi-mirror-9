#!/usr/bin/env python3
#
# Copyright 2015 Justin Wilson. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, this list of
#       conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright notice, this list
#       of conditions and the following disclaimer in the documentation and/or other materials
#       provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY JUSTIN WILSON ''AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL JUSTIN WILSON OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those of the
# authors and should not be interpreted as representing official policies, either expressed
# or implied, of Justin Wilson.
#

"""``capuchin`` is a simple wrapper around the tornado framework that
provides a few built-in endpoints (/ping, /status, /time) and also
some endpoint signing functions/wrappers.

Here is a simple service example app::

    import capuchin.web

    class TestHandler(tornado.web.RequestHandler):
            def get(self):
                    self.write("hola")

    def test_job():
            print("did some job")

    if __name__ == "__main__":
            c = capuchin.web.Application([
                    (r"/test", TestHandler),
            ])
            c.add_status_job("Test Job", 5, test_job)
            c.listen()
"""

import os

import tornado.ioloop
import tornado.web

from capuchin.handlers import StatusHandler, PingHandler, TimeHandler


class Application(tornado.web.Application):
    """tornado Application instance that auto-prepends each route
    with an endpoint set from the environment.

    eg. if the endpoint is `/myservice/1.0`, then the /ping route would be set as:
        `myservice/1.0/ping`

    Also includes built-in endpoints for the following:
        - /status (invokes each status job and writes the result as JSON)
        - /ping   (returns a 200 OK with `pong` as the body)
        - /time   (returns the servers current UTC time)
    """

    def __init__(self, handlers=None, **settings):
        # Set the port, defaulting to 8000
        try:
            port_str = os.environ.get("PORT", "8080")
            self.port = int(port_str)
        except ValueError:
            self.port = 8080

        # Set the host and endpoint
        self.address = os.environ.get("HOST", "0.0.0.0")
        self._endpoint = os.environ.get("ENDPOINT")
        self._jobs = []

        # Append the core handlers.
        all_handlers = [
            (r"/status", StatusHandler, dict(jobs_func=self.jobs)),
            (r"/ping", PingHandler),
            (r"/time", TimeHandler),
        ]
        if handlers:
            all_handlers = all_handlers + handlers
        super(Application, self).__init__(all_handlers, **settings)

    def jobs(self):
        """Generator that yields each status job.
        """
        for job in self._jobs:
            yield job

    def add_status_job(self, name, timeout, job_func):
        """Adds the given status job to the collection of jobs.
        """
        self._jobs.append((name, timeout, job_func,))

    # OVERRIDE
    def add_handlers(self, host_pattern, host_handlers):
        """Appends the given handlers to the collection.
        """
        host_handlers = prefix_handlers(self._endpoint, host_handlers)
        super(Application, self).add_handlers(host_pattern, host_handlers)

    # OVERRIDE
    def listen(self):
        """Starts an HTTP server on the on the host/port specified
        from the "HOST" and "PORT" environment variables.
        """
        if self.address:
            listening_on = "{}:{}".format(self.address, self.port)
            super(Application, self).listen(self.port, address=self.address)
        else:
            listening_on = "port {}".format(self.port)
            super(Application, self).listen(self.port)
        print("[capuchin] listening on " + listening_on)
        tornado.ioloop.IOLoop.instance().start()


def prefix_handlers(endpoint, handlers):
    """Prepends each handlers route with the given endpoint.

    eg.

    Given:
        endpoint    = /sweet+service/1.0
        handlers[0] = (r"/people, PeopleHandler)
    ------
    Result:
        handlers[0] = (r"/sweet+service/1.0/people", PeopleHandler)
    """
    if not endpoint:
        endpoint = '/'
    for i, handler in enumerate(handlers):
        path = handler[0]
        if path[0] == '/':
            path = path[1:]
        handlers[i] = (endpoint+path,)+handler[1:]
    return handlers
