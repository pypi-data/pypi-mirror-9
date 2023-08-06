# coding=utf8
from ..exc import BluelakeError
from ..protocol.const import *


class BLServerError(BluelakeError):

    def __init__(self, code, message=None):
        super(BLServerError, self).__init__(message)
        self.code = code


class ServiceNotExistError(BLServerError):

    def __init__(self, service_name):
        super(ServiceNotExistError, self).__init__(
            RESPONSE_CODE_SERVICE_NOT_FOUND,
            'Service {} could not be found'.format(service_name))


class MethodNotExistError(BLServerError):

    def __init__(self, method_name):
        super(MethodNotExistError, self).__init__(
            RESPONSE_CODE_SERVICE_NOT_FOUND,
            'Method {} could not be found'.format(method_name))


class ServerRunTimeError(BLServerError):
    """ Unexpected server run-time error. """

    def __init__(self, exc):
        super(ServerRunTimeError, self).__init__(
            RESPONSE_CODE_SYSTEM_ERROR,
            message=exc.message or 'System unknown error.')


class ServiceNameInvalidError(BLServerError):
    """ Unexpected server run-time error. """

    def __init__(self):
        super(ServiceNameInvalidError, self).__init__(
            RESPONSE_CODE_SYSTEM_ERROR,
            'Server\'s service name is not provided properly.')
