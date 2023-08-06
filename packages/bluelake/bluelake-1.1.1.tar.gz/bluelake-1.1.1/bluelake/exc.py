# coding=utf8


class BluelakeError(Exception):

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


class BLDiffRequestIdError(BluelakeError):

    def __init__(self):
        self.message = 'requestId in response is different from request.'
