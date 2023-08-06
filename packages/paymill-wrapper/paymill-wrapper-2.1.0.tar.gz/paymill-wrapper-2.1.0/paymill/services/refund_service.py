# coding=utf-8
from ..models.refund import Refund
from .paymill_service import PaymillService

__author__ = 'yalnazov'


class RefundService(PaymillService):
    def endpoint_path(self):
        return '/refunds'

    def paymill_object(self):
        return Refund

    def refund_transaction(self, transaction_id, amount, description=None):
        """Returns a remote Refund representation related to the transaction
        :param str transaction_id: the transaction id that we want to refund
        :param int amount: Amount (in cents) which will be refunded
        :param str or None description: additional description for this refund
        :return Refund: the fresh Refund object
        """
        return self.http_client('POST', params=dict(amount=amount, description=description),
                                url=self.endpoint_path() + '/' + transaction_id,
                                return_type=self.paymill_object())

    def detail(self, obj):
        """Returns/refreshes the remote Refund representation with that obj.id
        :param Refund obj: the Refund object with an id set
        :return Refund: the fresh Refund object
        """
        return self._detail(obj)