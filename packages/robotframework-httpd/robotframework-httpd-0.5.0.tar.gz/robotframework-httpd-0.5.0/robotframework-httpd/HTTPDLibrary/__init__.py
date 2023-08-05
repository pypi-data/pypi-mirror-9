# -*- coding: utf-8 -*-
import re
from threading import Thread
import time
import datetime

__author__ = 'mbbn'

import pkg_resources

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingMixIn
from robot.api import logger


class HTTPDLibrary(object):
    """

    """
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    __version__ = pkg_resources.get_distribution("robotframework-httpd").version

    def __init__(self, port, hostname='0.0.0.0'):
        self.httpd = ThreadedHTTPD((hostname, int(port)), RequestHandler)
        self.port = port
        self.httpd.fails = []

    def start_httpd(self):
        def run_server(httpd, port):
            try:
                logger.info("Start Http Server with port {}.".format(port), also_console=True)
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass
            logger.info("Http Server with port {} is stop.".format(port), also_console=True)
            httpd.shutdown()

        t = Thread(name=self.port, target=run_server, args=(self.httpd, self.port))
        t.daemon = True
        t.start()
        time.sleep(1)

    def stop_httpd(self):
        self.httpd.shutdown()

    def set_wished_request(self, wished_request):
        self.httpd.fails = []
        self.httpd.wished_request = wished_request

    def wait_to_receive_request(self, timeout=10):
        start = datetime.datetime.now()
        while datetime.datetime.now() < start + datetime.timedelta(seconds=int(timeout)):
            if len(self.httpd.fails) > 0:
                raise Exception(str(self.httpd.fails))
            true_all = True
            for key, value in self.httpd.wished_request.items():
                if value != True:
                    true_all = False
            if true_all:
                break
        if datetime.datetime.now() > start + datetime.timedelta(seconds=int(timeout)):
            raise Exception("Not Received Request after {} sec.".format(timeout))

    def wait_to_not_receive_request(self, timeout=10):
        start = datetime.datetime.now()
        while datetime.datetime.now() < start + datetime.timedelta(seconds=int(timeout)):
            if self.httpd.request_count > 0:
                t = datetime.datetime.now() - start
                raise Exception("Server with port {} received {} request after {}"
                                "".format(self.port, self.httpd.request_count, t))



class ThreadedHTTPD(ThreadingMixIn, HTTPServer):

    wished_request = None
    fails = None
    request_count = 0

    def verify_request(self, request, client_address):
        self.request_count += 1
        return HTTPServer.verify_request(self, request, client_address)


    def shutdown(self):
        HTTPServer.shutdown(self)

    def server_close(self):
        HTTPServer.server_close(self)

    def validate_request(self, method, path=None, body=None):
        wished_request = self.wished_request
        response_code = 200

        # check request method
        if wished_request["method"] != method:
            self.fails += ["Received method Not Equal Wished method.\n{} != {}"
                           "".format(method, wished_request["method"])]
            wished_request["method"] = False
            response_code = 400
        else:
            wished_request["method"] = True

        # check request path
        if "path" in wished_request:
            if wished_request["path"] != path:
                self.fails += ["Received Path Not Equal Wished path.    "
                               "\"{}\" != \"{}\""
                               "".format(path, wished_request["path"])]
                wished_request["path"] = False
                response_code = 400
            else:
                wished_request["path"] = True

        # check request post_body
        if "body" in wished_request:
            if not re.match(wished_request["body"], body):
                self.fails += ["Received body Not Equal Wished body.    "
                               "\"{}\" != \"{}\""
                               "".format(body, wished_request["body"])]
                wished_request["body"] = False
                response_code = 400
            else:
                wished_request["body"] = True

        return response_code

    def shutdown_request(self, request):
        HTTPServer.shutdown_request(self, request)

    def close_request(self, request):
        HTTPServer.close_request(self, request)


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        SimpleHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_GET(self):
        """Respond to a GET request."""
        content_len = int(self.headers.getheader('content-length', 0))
        body = self.rfile.read(content_len)
        response_code = self.server.validate_request("GET", self.path, body)
        self.send_response(response_code)

    def do_POST(self):
        """Respond to a POST request."""
        content_len = int(self.headers.getheader('content-length', 0))
        body = self.rfile.read(content_len)
        response = self.server.validate_request("POST", self.path, body)
        self.send_response(response)

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    http = HTTPDLibrary(5060)
    wished_request = {
        "method": "POST",
        "path": "/test",
        "body": "aadsa?d",

    }
    http.set_wished_request(wished_request)
    http.start_httpd()
    http.wait_to_receive_request(100)