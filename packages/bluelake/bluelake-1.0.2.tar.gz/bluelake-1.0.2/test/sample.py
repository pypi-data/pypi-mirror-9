# coding=utf8

from __future__ import absolute_import, division, print_function

from bluelake.client import (
    bl_service,
    bl_method,
)


@bl_service(name=u'sample')
class SampleService(object):

    def __init__(self, server):
        self.server = server

    @bl_method()
    def count(self, str):
        """

        :param str: str
        :return:    int
        """
        pass

    @bl_method()
    def bean(self, a, b, c, d):
        """

        :param a:   int
        :param b:   str
        :param c:   obj<SimpleBean>
        :param d:   dict<str, obj<SimpleBean>>
        :return:    list<>
        """
        pass

    @bl_method(name='returnNull')
    def return_null(self):
        """

        :return: ''
        """
        pass

    @bl_method(name='returnVoid')
    def return_void(self):
        """

        :return: ''
        """
        pass

    @bl_method(name='throwException')
    def throw_exception(self, additionalInfo, haha):
        """

        :param additionalInfo:  str
        :param haha:    str (BigDecimal)
        :return: SimpleException
        :exception: SimpleException
        """
        pass

    @bl_method(name='simpleMap')
    def simple_map(self, a):
        """

        :param a:   int
        :return:    map<int, obj<SimpleBean>>
        """
        pass

    @bl_method(name='complexMap')
    def complex_map(self, a):
        """

        :param a:   str
        :return:    map<str, list<obj<SimpleBean>>>
        """
        pass

    @bl_method(name='complexBean')
    def complex_bean(self, cb):
        """

        :param cb:  obj<ComplexBean>
        :return:    obj<ComplexBean>
        """
        pass
