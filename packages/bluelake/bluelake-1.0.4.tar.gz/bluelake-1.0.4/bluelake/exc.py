# coding=utf8

from __future__ import absolute_import, division, print_function


class BluelakeExc(Exception):

    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return self.msg


class URLInvalidExc(BluelakeExc):

    def __init__(self, msg=''):
        self.msg = msg + ' e.g. 192.168.1.2:8088 or google.com:80'
        super(URLInvalidExc, self).__init__(self.msg)
