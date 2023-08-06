# coding=utf-8
__author__ = 'yalnazov'


class PMError(Exception):

    """

    Represents a PAYMILL API error returned with raw message and http code.

    """

    def __init__(self, message='Unknown', http_code='-1'):
        self.message = message
        self.http_code = http_code

    def __str__(self):
        return repr(str(self.message) + str(self.http_code))