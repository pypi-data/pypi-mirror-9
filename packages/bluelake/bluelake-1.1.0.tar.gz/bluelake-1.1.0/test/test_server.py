# -*- coding: utf-8 -*-
from bluelake.server.exc import ServiceNotExistError
from bluelake.server.http import BLSimpleServer


HOST_NAME = 'localhost'  # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8080  # Maybe set this to 9000.

RESPONSE_HEADERS = {
    "Content-type": "application/json; charset=UTF-8",
    "": "application/json",
}


class SimpleBean(object):

    def __init__(self, number=None, lulu=None, number2=None, double1=None,
                 bd=None, ts=None):

        self.number = number
        self.lulu = lulu
        self.number2 = number2
        self.double1 = double1
        self.bd = bd
        self.ts = ts


class ComplexBean(object):

    def __init__(self, simpleBean, number):
        self.simpleBean = simpleBean
        self.number = number


class Example:

    service = 'sample'

    def count(self, str):
        return len(str)

    def bean(self, a, b, c, d):
        list = []
        list.append(c)
        list.append(None)
        list.append(d.get(b))
        return list

    def returnNull(self):
        return None

    def throwException(self, additionalInfo, haha):
        raise ServiceNotExistError('service xxx')

    def runtimeException(self):
        raise RuntimeError('test run time error')

    def simpleMap(self, a):
        bean = SimpleBean(number=a)
        return {1: bean}

    def complexBean(self, cb):
        return cb

    def complexMap(self, a):
        simple = SimpleBean(number=len(a))
        return {a: [simple]}


class Example2:

    service = 'sample2'

    def count(self, string):
        return len(string) * 10


if __name__ == '__main__':
    server = BLSimpleServer('localhost', 8000, (Example(), Example2()))
    server.serve()