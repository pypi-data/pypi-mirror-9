# coding=utf-8
from jsonobject import *
from .order import Order
from .filter import Filter
__author__ = 'yalnazov'


class Refund(JsonObject):
    id = StringProperty()
    """:type str: Unique identifier of this refund."""

    transaction = None
    """:type Transaction: transaction object"""

    amount = IntegerProperty()
    """:type int (>0): The refunded amount."""

    status = StringProperty()
    """:type enum(open, pending, refunded): Indicates the current status of this transaction."""

    description = StringProperty()
    """:type str or None: The description given for this refund."""

    livemode = BooleanProperty()
    """:type boolean: Whether this refund happend in test- or in livemode."""

    created_at = IntegerProperty()
    """:type int: Unix-Timestamp for the creation date."""

    updated_at = IntegerProperty()
    """:type int: Unix-Timestamp for the last update."""

    app_id = StringProperty()
    """:type str or None: App (ID) that created this refund or null if created by yourself."""

    def updatable_fields(self):
        return

    class Order(Order):
        @classmethod
        def transaction(cls):
            """Creates and returns an transaction Order
            :return: Order object
            """
            return Order(typ='transaction')

        @classmethod
        def client(cls):
            """Creates and returns an client Order
            :return: Order object
            """
            return Order(typ='client')

        @classmethod
        def amount(cls):
            """Creates and returns an amount Order
            :return: Order object
            """
            return Order(typ='amount')

        @classmethod
        def created_at(cls):
            """Creates and returns an created_at Order
            :return: Order object
            """
            return Order(typ='created_at')

    class Filter(Filter):
        @classmethod
        def by_client_id(cls, client_id):
            """Creates and returns an client Filter
            :param str client_id: the client id to filter by
            :return: Filter object
            """
            return Filter('client', values=(client_id,), operator=Filter.OPERATOR['EQUAL'])

        @classmethod
        def by_transaction_id(cls, transaction_id):
            """Creates and returns an transaction Filter
            :param int transaction_id: transaction id to filter by
            :return: Filter object
            """
            return Filter('transaction', values=(transaction_id,), operator=Filter.OPERATOR['EQUAL'])

        @classmethod
        def by_amount(cls, amount):
            """Creates and returns an amount Filter
            :param int amount: the amount to filter by
            :return: Filter object
            """
            return Filter('amount', values=(amount,), operator=Filter.OPERATOR['EQUAL'])

        @classmethod
        def by_amount_greater_than(cls, amount):
            """Creates and returns a greater than amount Filter
            :param int amount: the amount to filter by
            :return: Filter object
            """
            return Filter('amount', values=(amount,), operator=Filter.OPERATOR['GREATER_THAN'])

        @classmethod
        def by_amount_less_than(cls, amount):
            """Creates and returns a less than amount Filter
            :param int amount: the amount to filter by
            :return: Filter object
            """
            return Filter('amount', values=(amount,), operator=Filter.OPERATOR['LESS_THAN'])


        @classmethod
        def by_created_at(cls, from_date, to_date=None):
            """Creates and returns an from_date-to_date Filter or from_date Filter for the created_at field
            :param int from_date: the from_date to filter by
            :param int to_date:the to_date to filter by
            :return: Filter object
            """
