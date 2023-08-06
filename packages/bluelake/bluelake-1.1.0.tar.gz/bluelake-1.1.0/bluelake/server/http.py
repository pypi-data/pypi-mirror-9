# coding=utf8
import time
import logging
import BaseHTTPServer
from SocketServer import (
    ThreadingMixIn,
    ForkingMixIn,
)

from . import BLServerBase, BLRequestHandlerBase
from ..protocol.const import *
from ..protocol.utils import parse_request
from ..protocol.response import make_response


class BLHTTPServerBase(BaseHTTPServer.HTTPServer, BLServerBase):
    """ Bluelake HTTP server base """

    def __init__(self, host, port, handlers):
        BaseHTTPServer.HTTPServer.__init__(self, (host, port), BLHTTPHandler)
        BLServerBase.__init__(self, host, port, handlers)

    def serve(self):
        logging.info("%s Server starts on %s:%s" %
                     (time.asctime(), self.host, self.port))
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            logging.exception('interrupted')
        except Exception as e:
            logging.exception(e)
        finally:
            self.server_close()


class BLSimpleServer(BLHTTPServerBase):
    """ Simple single-threaded HTTP server. """
    pass


class BLThreadingServer(ThreadingMixIn, BLHTTPServerBase):
    """ Nonblock multi-threading HTTP server. """
    pass


class BLForkingServer(ForkingMixIn, BLHTTPServerBase):
    """ Nonblock multi-processing HTTP server. """
    pass


class BLHTTPHandler(BLRequestHandlerBase):

    def do_POST(self):
        """ Handle POST request. """

        post_body = self._get_post_body()
        request = parse_request(post_body)
        try:
            result = self.server.processor.do_process(
                request['content']['service'],
                request['content']['method'],
                request['content']['argMap']
            )
        except Exception as x:
            result = x
        response_json = make_response(request['requestId'], result, )

        self._make_response(response_json)

    def _get_post_body(self):
        content_len = int(self.headers.getheader('content-length', 0))
        return self.rfile.read(content_len)

    def _make_response(self, data, status_code=200):
        self.send_response(status_code)
        for name, value in JSON_HEADERS.iteritems():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(data)
