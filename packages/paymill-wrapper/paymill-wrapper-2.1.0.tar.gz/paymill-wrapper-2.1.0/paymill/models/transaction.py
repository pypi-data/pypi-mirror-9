# coding=utf-8
from jsonobject import *
from .order import Order
from .filter import Filter
from .invoice import Invoice
from .payment import Payment
from .client import Client
from .preauthorization import Preauthorization
from .fee import Fee
__author__ = 'yalnazov'


class Transaction(JsonObject):
    id = StringProperty()
    """:type str: Unique identifier of this transaction."""

    amount = IntegerProperty()
    """:type str: Formatted amount of this transaction."""

    origin_amount = IntegerProperty()
    """:type int (>0): The used amount, smallest possible unit per currency
       (for euro, we’re calculating the amount in cents)."""

    currency = StringProperty()
    """:type str: ISO 4217 formatted currency code."""

    status = StringProperty()
    """:type enum(open, pending, closed, failed, partial_refunded, refunded, preauthorize, chargeback)
    Indicates the current status of this transaction, e.g closed means the transaction is
    successfully transferred, refunded means that the amount is fully or in parts refunded."""

    description = StringProperty()
    """:type str or None: Need a additional description for this transaction?
    Maybe your shopping cart ID or something like that?"""

    livemode = BooleanProperty()
    """:type boolean: Whether this transaction was issued while being in live mode or not."""

    is_fraud = BooleanProperty()
    """:type boolean: The transaction is marked as fraud or not."""

    refunds = ListProperty()
    """:type list or None: Refund objects or null"""

    payment = ObjectProperty(Payment)
    """:type Payment object or None"""

    client = ObjectProperty(Client)
    """:type Client object or None"""

    preauthorization = ObjectProperty(Preauthorization)
    """:type Preauthorization object or null"""

    created_at = IntegerProperty()
    """:type int: Unix-Timestamp for the creation date."""

    updated_at = IntegerProperty()
    """:type int: Unix-Timestamp for the last update."""

    response_code = IntegerProperty()
    """:type int: Response code"""

    short_id = StringProperty()
    """:type str: Unique identifier of this transaction provided to the acquirer for the statements."""

    invoices = ListProperty()
    """:type list or None: PAYMILL invoice where the transaction fees are charged."""

    fees = ListProperty(Fee)
    """:type list or None: App fees or null."""

    app_id = StringProperty()
    """:type str or None: App (ID) that created this refund or null if created by yourself."""

    def updatable_fields(self):
        return 'description'

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
        def by_description(cls, description):
            """Creates and returns an description Filter
            :param str description: the description to filter by
            :return: Filter object
            """
            return Filter('description', values=(description,), operator=Filter.OPERATOR['EQUAL'])

        @classmethod
        def by_created_at(cls, from_date, to_date=None):
            """Creates and returns an from_date-to_date Filter or from_date Filter for the created_at field
            :param int from_date: the from_date to filter by
            :param int to_date:the to_date to filter by
            :return: Filter object
            """
            return Filter('created_at', values=(from_date, to_date), operator=Filter.OPERATOR['INTERVAL'])

        @classmethod
        def by_updated_at(cls, from_date, to_date=None):
            """Creates and returns an from_date-to_date Filter or from_date Filter for the updated_at field
            :param int from_date: the from_date to filter by
            :param int to_date:the to_date to filter by
            :return: Filter object
            """
            return Filter('updated_at', values=(from_date, to_date), operator=Filter.OPERATOR['INTERVAL'])

        @classmethod
        def by_status(cls, status):
            """Creates and returns a status Filter
            :param str status: the status to filter by
            :return: Filter object
            """
            return Filter('status', values=(status,), operator=Filter.OPERATOR['EQUAL'])