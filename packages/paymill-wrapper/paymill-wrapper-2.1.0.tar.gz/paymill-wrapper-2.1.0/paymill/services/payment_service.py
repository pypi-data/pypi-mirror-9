# coding=utf-8
from ..models.payment import Payment
from .paymill_service import PaymillService
__author__ = 'yalnazov'


class PaymentService(PaymillService):
    def endpoint_path(self):
        return '/payments'

    def paymill_object(self):
        return Payment

    def create(self, token, client_id=None):
        """Creates a remote Payment object representation
        :param str token: Unique credit card token
        :param client_id: Client unique identifier
        :return Payment: the removed Payment object
        """
        params = dict(token=token, client=client_id)
        return self._create(params)

    def detail(self, obj):
        """Returns/refreshes the remote Payment representation with that obj.id
        :param Payment obj: the Payment object with an id set
        :return Payment: the fresh Payment object
        """
        return self._detail(obj)

    def remove(self, obj):
        """Removes a remote Payment representation with that obj.id
        :param Payment obj: the Payment object with an id set
        :return Payment: the removed Payment object
        """
        return self._remove(obj)