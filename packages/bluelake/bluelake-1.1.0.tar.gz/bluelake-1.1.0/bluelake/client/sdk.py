# coding=utf8
from .exc import *
from .rpc import rpc


class BluelakeSDK(object):

    def __init__(self, service_name, server_url):
        self.service = service_name
        self.server = server_url

    def __getattr__(self, method_name):

        def tmp_method(*args, **kwargs):
            if args:
                raise BLPositionBasedParamError()
            return rpc(
                self.server,
                self.service,
                method_name,
                kwargs
            )
        return tmp_method
