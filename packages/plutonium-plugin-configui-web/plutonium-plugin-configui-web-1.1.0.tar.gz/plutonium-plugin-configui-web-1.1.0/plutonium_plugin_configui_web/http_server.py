import BaseHTTPServer
from SocketServer import ThreadingMixIn

# HTTP server with timeout settings
class AdvancedHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):

    def __init__(self, listen, handler, request_timeout = 0):
        BaseHTTPServer.HTTPServer.__init__(self, listen, handler)
        self.request_timeout = request_timeout

    def set_request_timeout(self, value):
        self.request_timeout = value

    def finish_request(self, request, client_address):
        request.settimeout(self.request_timeout)
        # "super" can not be used because BaseServer is not created from object
        BaseHTTPServer.HTTPServer.finish_request(self, request, client_address)
