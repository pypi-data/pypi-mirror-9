# coding=utf8
from .const import *
from .utils import JsonMixIn


class BLProtocol(JsonMixIn):
    """ Bluelake Protocol model

    tips:
    Any attributes begin without '__'(double underline) is counted in protocol.

    """

    def __init__(self, type, version=None, format=None,
                 requestId=None, content=''):

        self.type = type
        self.version = version or CURRENT_VERSION
        self.format = format or DEFAULT_FORMAT
        self.requestId = requestId
        self.content = content
