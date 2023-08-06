# -*- coding: utf-8 -*-
import functools
import inspect
from .rpc import rpc


def JsonService(name=None):
    """ Decorators for Bluelake service class

    :param name: BlueLake service name or None using class name
    :return:
    """
    def deco_cls_func(cls):
        cls.service_name = name if name else cls.__name__
        return cls
    return deco_cls_func


def JsonMethod(name=None):
    """ Decorators for Bluelake methods

    :param name: method's name or None using default func_name
    :return:
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            method_name = func.func_name if not name else name
            arg_map = _get_key_value_args(func, args, kwargs)

            return rpc(
                self.server,
                type(self).service_name,
                method_name,
                arg_map
            )
        return wrapper

    return decorator


def _get_key_value_args(func, args, kwargs):
    arg_map = {}
    if kwargs:
        arg_map.update(kwargs)

    if args:
        argspec = inspect.getargspec(func)
        for index, value in enumerate(args):
            arg_map.__setitem__(argspec[0][index+1], value)

    return arg_map
