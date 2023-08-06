# coding=utf8

from __future__ import absolute_import, division, print_function


class BluelakeExc(Exception):

    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return self.msg
