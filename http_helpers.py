from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

    # print request.error_code       # None  (check this first)
    # print request.command          # "GET"
    # print request.path             # "/who/ken/trust.html"
    # print request.request_version  # "HTTP/1.1"
    # print len(request.headers)     # 3
    # print request.headers.keys()   # ['accept-charset', 'host', 'accept']
    # print request.headers['host']  # "cm.bell-labs.com"
