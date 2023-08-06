# coding=utf-8
from ..models.preauthorization import Preauthorization
from .paymill_service import PaymillService
__author__ = 'yalnazov'


class PreauthorizationService(PaymillService):
    def endpoint_path(self):
        return '/preauthorizations'

    def paymill_object(self):
        return Preauthorization

    def create_with_token(self, token, amount, currency, description=None):
        """Creates a remote Preauthorization object representation
        :param str token: A token generated through our JavaScript-Bridge
        :param int amount: Amount (in cents) which will be charged
        :param str currency: ISO 4217 formatted currency code
        :param str client_id or None: The identifier of a client
        :param int fee_amount or None: Fee included in the transaction amount (set by a connected app).
        :param str fee_payment_id or None: The identifier of the payment from which the fee will be charged
        :param str fee_currency or None: The currency of the fee (e.g. EUR, USD). If it´s not set, the currency of
               the transaction is used. We suggest to always use as it might cause problems, if your account does not
               support the same currencies as your merchants accounts.
        :return Preauthorization: the created Preauthorization object
        """
        if token is None:
            raise ValueError('Token is None!')

        return self._create_preauthorization(dict(token=token), amount, currency, description)

    def create_with_payment_id(self, payment_id, amount, currency, description=None):
        """Creates a remote Preauthorization object representation
        :param str payment_id: The identifier of a payment
        :param int amount: Amount (in cents) which will be charged
        :param str currency: ISO 4217 formatted currency code
        :param str client_id or None: The identifier of a client
        :param str or None description: Description for this preauthorization
        :return Preauthorization: the created Preauthorization object
        """
        if payment_id is None:
            raise ValueError('Payment id is None!')

        return self._create_preauthorization(dict(payment=payment_id), amount, currency, description)

    def _create_preauthorization(self, params, amount, currency, description):
        if amount is None or currency is None:
            raise ValueError('Amount or currency None!')

        params.update(amount=amount, currency=currency, description=description)

        return self._create(params)

    def detail(self, obj):
        """Returns/refreshes the remote Preauthorization representation with that obj.id
        :param Preauthorization obj: the Preauthorization object with an id set
        :return Preauthorization: the fresh Preauthorization object
        """
        return self._detail(obj)

    def update(self, obj):
        """Updates and returns a Preauthorization object according to its updatable fields
        :param Preauthorization obj: the Preauthorization object to update
        :return Preuthorization: the updated Preauthorization object
        """
        return self._update(obj)

    def remove(self, obj):
        """Removes a remote Preauthorization representation with that obj.id
        :param Preauthorization obj: the Preauthorization object with an id set
        :return Preauthorization: the removed Preauthorization object
        """
        return self._remove(obj)