# coding=utf-8
from .order import Order
from .filter import Filter
from .payment import Payment
from .client import Client
from jsonobject import *
__author__ = 'yalnazov'


class Preauthorization(JsonObject):
    id = StringProperty()
    """:type str: Unique identifier of this preauthorization"""

    description = StringProperty()
    """:type str or None: Description for this preauthorization"""

    amount = StringProperty()
    """:type str: Formatted amount which will be reserved for further transactions"""

    status = StringProperty()
    """:type enum(open, pending, closed, failed, deleted, preauth):
    Indicates the current status of this preauthorization"""

    livemode = BooleanProperty()
    """:type boolean: Whether this preauthorization was issued while being in live mode or not"""

    payment = ObjectProperty(Payment)
    """:type Payment object or None"""

    client = ObjectProperty(Client)
    """:type Client object or None"""

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
        def by_payment_id(cls, payment_id):
            """Creates and returns an payment Filter
            :param int payment_id: payment id to filter by
            :return: Filter object
            """
            return Filter('transaction', values=(payment_id,), operator=Filter.OPERATOR['EQUAL'])

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
            return Filter('created_at', values=(from_date, to_date), operator=Filter.OPERATOR['INTERVAL'])