from gzip import GzipFile
from StringIO import StringIO

import urllib2


class UserAgentProcessor(urllib2.BaseHandler):
    """A handler to add a custom UA string to urllib2 requests
    """

    def __init__(self, uastring):
        self.handler_order = 100
        self.ua = uastring

    def http_request(self, request):
        request.add_header("User-Agent", self.ua)
        return request

    https_request = http_request


class GZipProcessor(urllib2.BaseHandler):
    """
    A handler to add gzip capabilities to urllib2 requests
    http://techknack.net/python-urllib2-handlers/
    """

    def http_request(self, req):
        req.add_header("Accept-Encoding", "gzip")
        return req

    https_request = http_request

    def http_response(self, req, resp):
        if resp.headers.get("content-encoding") == "gzip":
            gz = GzipFile(
                fileobj=StringIO(resp.read()),
                mode="r"
            )
            old_resp = resp
            resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
            resp.msg = old_resp.msg

        return resp

    https_response = http_response
