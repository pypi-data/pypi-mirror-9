# coding=utf-8
__author__ = 'yalnazov'

from abc import abstractmethod, ABCMeta
from six import with_metaclass


class AbstractHTTPClient(with_metaclass(ABCMeta, object)):

    """Abstract base class for HTTP clients.

    Purpose of this class is to give developers to change the used HTTP client with other of their liking without
    changing the core of the PAYMILL Python wrapper.
    Don't use this class directly. This class should be used as an interface and should be subclassed only.

    """

    @abstractmethod
    def __init__(self, base_url, user_name, user_pass, timeout=5):
        return

    @abstractmethod
    def get(self, params, url, return_type):
        return

    @abstractmethod
    def post(self, paraxms, url, return_type):
        return

    @abstractmethod
    def put(self, params, url, return_type):
        return

    @abstractmethod
    def delete(self, params, url, return_type):
        return