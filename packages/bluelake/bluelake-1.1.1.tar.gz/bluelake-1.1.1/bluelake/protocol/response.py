# coding=utf8
from .const import *
from .protocol import BLProtocol
from .utils import to_bluelake_json


class BLResponseExc:

    def __init__(self, _type=None, _message=None, _stack_trace=None,
                 _cause=None):

        self._type = _type
        self._message = _message
        self._stack_trace = _stack_trace
        self._cause = _cause
        # self._others = exc_info


class BLResponse(BLProtocol):
    def __init__(self, request_id, data, code, version=None,
                 format=None, msg_type=None):
        self.__code = code
        self.__data = data
        msg_type = msg_type or TYPE_SYNC_RESPONSE
        content = {'code': code, 'data': to_bluelake_json(data)}
        super(BLResponse, self).__init__(
            msg_type, version, format, request_id, to_bluelake_json(content))

    def get_data(self):
        return self.__data

    def get_code(self):
        return self.__code


def make_response(request_id, data):
    """ Return bluelake json-formatted response """

    response_data = data
    code = RESPONSE_CODE_OK
    if isinstance(data, Exception):
        response_data = BLResponseExc(_message=data.message,
                                      _type=data.__class__.__name__,
                                      _cause=data.__class__.__name__)
        code = getattr(data, 'code', RESPONSE_CODE_SYSTEM_ERROR)

    return BLResponse(request_id, response_data, code).to_json()
