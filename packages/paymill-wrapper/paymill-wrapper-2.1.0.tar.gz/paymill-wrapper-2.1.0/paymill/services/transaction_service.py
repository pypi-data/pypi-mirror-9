# coding=utf-8
from ..models.transaction import Transaction
from .paymill_service import PaymillService
__author__ = 'yalnazov'


class TransactionService(PaymillService):
    def endpoint_path(self):
        return '/transactions'

    def paymill_object(self):
        return Transaction

    def create_with_token(self, token, amount, currency, description, client_id=None,
                          fee_amount=None, fee_payment_id=None, fee_currency=None):
        """Creates a remote Transaction object representation
        :param str token: A token generated through our JavaScript-Bridge
        :param int amount: Amount (in cents) which will be charged
        :param str currency: ISO 4217 formatted currency code
        :param str client_id or None: The identifier of a client
        :param int fee_amount or None: Fee included in the transaction amount (set by a connected app).
        :param str fee_payment_id or None: The identifier of the payment from which the fee will be charged
        :param str fee_currency or None: The currency of the fee (e.g. EUR, USD). If it´s not set, the currency of
               the transaction is used. We suggest to always use as it might cause problems, if your account does not
               support the same currencies as your merchants accounts.
        :return Transaction: the created Transaction object
        """
        if token is None:
            raise ValueError('Token is None!')

        return self._create_transaction(dict(token=token), amount, currency, description,
                                        client_id, fee_amount, fee_payment_id, fee_currency)

    def create_with_payment_id(self, payment_id, amount, currency, description, client_id=None,
                               fee_amount=None, fee_payment_id=None, fee_currency=None):
        """Creates a remote Transaction object representation
        :param str payment_id: The identifier of a payment
        :param int amount: Amount (in cents) which will be charged
        :param str currency: ISO 4217 formatted currency code
        :param str client_id or None: The identifier of a client
        :param int fee_amount or None: Fee included in the transaction amount (set by a connected app).
        :param str fee_payment_id or None: The identifier of the payment from which the fee will be charged
        :param str fee_currency or None: The currency of the fee (e.g. EUR, USD). If it´s not set, the currency of
               the transaction is used. We suggest to always use as it might cause problems, if your account does not
               support the same currencies as your merchants accounts.
        :return Transaction: the created Transaction object
        """
        if payment_id is None:
            raise ValueError('Payment id is None!')

        return self._create_transaction(dict(payment=payment_id), amount, currency, description,
                                        client_id, fee_amount, fee_payment_id, fee_currency)

    def create_with_preauthorization_id(self, preauthorization_id, amount, currency, description, client_id=None,
                                        fee_amount=None, fee_payment_id=None, fee_currency=None):
        """Creates a remote Transaction object representation
        :param str preauthorization_id: The identifier of a Preauthorization
        :param int amount: Amount (in cents) which will be charged
        :param str currency: ISO 4217 formatted currency code
        :param str client_id or None: The identifier of a client
        :param int fee_amount or None: Fee included in the transaction amount (set by a connected app).
        :param str fee_payment_id or None: The identifier of the payment from which the fee will be charged
        :param str fee_currency or None: The currency of the fee (e.g. EUR, USD). If it´s not set, the currency of
               the transaction is used. We suggest to always use as it might cause problems, if your account does not
               support the same currencies as your merchants accounts.
        :return Transaction: the created Transaction object
        """
        if preauthorization_id is None:
            raise ValueError('Preauthorization id is None!')

        return self._create_transaction(dict(payment=preauthorization_id), amount, currency, description,
                                        client_id, fee_amount, fee_payment_id, fee_currency)

    def _create_transaction(self, params, amount, currency, description, client_id=None, fee_amount=None,
                            fee_payment_id=None, fee_currency=None):
        if amount is None or currency is None:
            raise ValueError('Amount or currency None!')

        params.update(amount=amount, currency=currency, description=description, client=client_id, fee_payment=fee_payment_id,
                      fee_amount=fee_amount, fee_currency=fee_currency)

        return self._create(params)

    def detail(self, obj):
        """Returns/refreshes the remote Transaction representation with that obj.id
        :param Transaction obj: the Transaction object with an id set
        :return Transaction: the fresh Transaction object
        """
        return self._detail(obj)

    def update(self, obj):
        """Updates and returns a Transaction object according to its updatable fields
        :param Transaction obj: the Transaction object to update
        :return Transaction: the updated Transaction object
        """
        return self._update(obj)