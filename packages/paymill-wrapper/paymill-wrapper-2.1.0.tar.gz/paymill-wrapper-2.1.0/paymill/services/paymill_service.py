# coding=utf-8
__author__ = 'yalnazov'

from abc import ABCMeta, abstractproperty
from ..models.paymill_list import PaymillList
from six import with_metaclass, iteritems


class PaymillService(with_metaclass(ABCMeta, object)):

    """Abstract Base Classes(ABC) for all PAYMILL services.

    Do not use this class directly.

    """

    @abstractproperty
    def endpoint_path(self):
        return

    @abstractproperty
    def paymill_object(self):
        return

    def __init__(self, http_client):
        self.http_client = http_client

    def _create(self, params):
        return self.http_client('POST', params, self.endpoint_path(), self.paymill_object())

    def _detail(self, obj):
        return self.http_client('GET', params=None, url=self.endpoint_path() + '/' + obj.id,
                                return_type=self.paymill_object())

    def _update(self, obj, **kwargs):
        update_dict = dict()
        #pack all updatable object's fields in the update_dict
        for u in obj.updatable_fields():
            if obj[u] is not None:
                if hasattr(obj[u], 'id'):
                    update_dict.update(**{str(u): obj[u].id})
                else:
                    update_dict.update(**{str(u): obj[u]})
        #pack all special updatable object's fields in the update_dict
        for k, v in iteritems(kwargs):
            update_dict.update(**{k: v})

        return self.http_client('PUT', update_dict, self.endpoint_path() + '/' + obj.id,
                                self.paymill_object())

    def _list(self, **kwargs):
        return self.http_client('GET', dict(**kwargs), self.endpoint_path(), PaymillList)

    def _remove(self, obj, params=None):
        return self.http_client('DELETE', params, url=self.endpoint_path() + '/' + obj.id,
                                return_type=self.paymill_object())

    def list(self, count=None, offset=None, filtr=None, order=None):
        """Returns a remote representation of a PAYMILL List
        :param int count: list count
        :param int offset: list offset
        :param Filter filtr:
        :param Order order:
        :return: PaymillList
        """
        params = dict(count=count, offset=offset)
        if order is not None:
            params.update(order.to_dict())
        if filtr is not None:
            params.update(filtr.to_dict())

        return self._list(**params)
