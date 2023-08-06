# coding=utf8
from collections import defaultdict
import inspect
from .exc import (
    MethodNotExistError,
    ServiceNotExistError,
    ServiceNameInvalidError)


def _parse_methods(handler):
    """ Parse methods in handler object.

    :param handler: service object
    :return: methods dict
    """
    methods = inspect.getmembers(handler.__class__,
                                 predicate=inspect.ismethod)
    # get rid of methods those not start with '_' or '__'
    methods = filter(lambda m: not m[0].startswith('_'), methods)

    return {method[0]: method[1] for method in methods}


def _get_service_name(handler_obj):
    """ Get service name in handler object """
    svc_name = getattr(handler_obj, 'service',
                       handler_obj.__class__.__name__)

    if not isinstance(svc_name, basestring):
        raise ServiceNameInvalidError()

    return svc_name


class BLProcessor(object):
    """
    @attribute services:
    """

    def __init__(self, handlers):
        self.services = {}
        if type(handlers) not in (tuple, list, set):
            # single-handler
            svc_name = _get_service_name(handlers)
            self.services.__setitem__(svc_name,
                                      [handlers, _parse_methods(handlers)])
        else:
            # multi-handler
            for handler in handlers:
                svc_name = _get_service_name(handler)
                self.services.__setitem__(svc_name,
                                          [handler, _parse_methods(handler)])

    def do_process(self, svc_name, method_name, kwargs):
        service = self.services.get(svc_name, None)
        if service is None:
            raise ServiceNotExistError(svc_name)

        method = service[1].get(method_name, None)
        if method is None:
            raise MethodNotExistError(method_name)

        return method(service[0], **kwargs)
