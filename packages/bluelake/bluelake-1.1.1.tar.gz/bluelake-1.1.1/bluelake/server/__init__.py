# coding=utf8
import BaseHTTPServer

from .process import BLProcessor


class BLServerBase(object):
    """ Bluelake server base """

    def __init__(self, host, port, handlers):
        self.host = host
        self.port = port
        self.processor = BLProcessor(handlers)

    def serve(self):
        """ Main serve loop """
        pass


class BLRequestHandlerBase(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_POST(self):
        raise NotImplementedError(
            'Bluelake handler must implement \'do_POST\' method')
