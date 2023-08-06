# coding=utf8
import uuid

from .const import *
from .protocol import BLProtocol
from .utils import to_bluelake_json


class BLRequestData(object):

    def __init__(self, service, method, arg_map=None):
        self.service = service
        self.method = method

        if arg_map is not None:
            for name, value in arg_map.iteritems():
                arg_map.__setitem__(name, to_bluelake_json(value))
            self.argMap = arg_map

    def to_json(self):
        return to_bluelake_json(self)


class BLRequest(BLProtocol):

    def __init__(self, service, method, arg_map=None,
                 version=None, format=None, msg_type=None):

        msg_type = msg_type or TYPE_SYNC_REQUEST
        request_id = uuid.uuid1().__str__()
        self.content = BLRequestData(service, method, arg_map).to_json()

        super(BLRequest, self).__init__(msg_type, version, format, request_id,
                                        self.content)
