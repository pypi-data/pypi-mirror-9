# -*- coding: utf-8 -*-
# leap.common.testing.https_server.py
# Copyright (C) 2013 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
A simple HTTPS server to be used in tests
"""
from BaseHTTPServer import HTTPServer
import os
import ssl
import SocketServer
import threading
import unittest

_where = os.path.split(__file__)[0]


def where(filename):
    return os.path.join(_where, filename)


class HTTPSServer(HTTPServer):
    def server_bind(self):
        SocketServer.TCPServer.server_bind(self)
        self.socket = ssl.wrap_socket(
            self.socket, server_side=True,
            certfile=where("leaptestscert.pem"),
            keyfile=where("leaptestskey.pem"),
            ca_certs=where("cacert.pem"),
            ssl_version=ssl.PROTOCOL_SSLv23)


class TestServerThread(threading.Thread):
    def __init__(self, test_object, request_handler):
        threading.Thread.__init__(self)
        self.request_handler = request_handler
        self.test_object = test_object

    def run(self):
        self.server = HTTPSServer(('localhost', 0), self.request_handler)
        host, port = self.server.socket.getsockname()
        self.test_object.HOST, self.test_object.PORT = host, port
        self.test_object.server_started.set()
        self.test_object = None
        try:
            self.server.serve_forever(0.05)
        finally:
            self.server.server_close()

    def stop(self):
        self.server.shutdown()


class BaseHTTPSServerTestCase(unittest.TestCase):
    """
    derived classes need to implement a request_handler
    """
    def setUp(self):
        self.server_started = threading.Event()
        self.thread = TestServerThread(self, self.request_handler)
        self.thread.start()
        self.server_started.wait()

    def tearDown(self):
        self.thread.stop()

    def get_server(self):
        host, port = self.HOST, self.PORT
        if host == "127.0.0.1":
            host = "localhost"
        return "%s:%s" % (host, port)


if __name__ == "__main__":
    unittest.main()
