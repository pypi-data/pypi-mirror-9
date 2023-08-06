# coding=utf8
from ..exc import *


class BLClientError(BluelakeError):
    pass


class URLInvalidError(BLClientError):

    def __init__(self, message=''):
        self.message = message + ' e.g. 192.168.1.2:8088 or google.com:80'


class BLPositionBasedParamError(BLClientError):

    def __init__(self):
        self.message = 'Bluelake does not support position-based parameters,' \
                       ' please use key-valued parameters instead.'


class ConnectionError(BLClientError):

    def __init__(self, message=None):
        self.message = message or 'Connect refused,please check your url again.'
