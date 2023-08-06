# coding=utf-8
from .order import Order
from .filter import Filter
from jsonobject import *
from . import client
__author__ = 'yalnazov'


class Payment(JsonObject):

    id = StringProperty()
    """:type str: Unique identifier for this credit card payment"""

    type = StringProperty()
    """:type enum(creditcard,debit)"""

    client = None

    """:type str or None: Client object"""

    card_type = StringProperty()
    """:type str: Card type eg. visa, mastercard"""

    country = StringProperty()
    """:type str or None: Country"""

    expire_month = StringProperty()
    """:type str: Expiry month of the credit card"""

    expire_year = StringProperty()
    """:type str: Expiry year of the credit card"""

    card_holder = None
    """:type str: Name of the card holder"""

    last4 = StringProperty()
    """:type str: The last four digits of the credit card"""

    code = StringProperty()
    """":type str: The used Bank Code"""

    account = StringProperty()
    """:type str: The used account number, for security reasons the number is masked"""

    holder = StringProperty()
    """:type str: Name of the account holder"""

    created_at = IntegerProperty()
    """:type int: Unix-Timestamp for the creation date"""

    updated_at = IntegerProperty()
    """:type int: Unix-Timestamp for the last update"""

    is_recurring = BooleanProperty()
    """:type boolean: The payment is recurring (can be used more than once)."""

    is_usable_for_preauthorization = BooleanProperty()
    """:type boolean: The payment is usable for preauthorization."""

    app_id = StringProperty()
    """:type str or None: App (ID) that created this refund or null if created by yourself."""

    #dynamic JSON to Python representation
    def __getattribute__(self, name):
        if name == 'client':
            attr = object.__getattribute__(self, name)
            if isinstance(attr, str):
                return client.Client(id=attr)
            if isinstance(attr, dict):
                return client.Client(attr)

        return object.__getattribute__(self, name)

    def updatable_fields(self):
        pass

    class Order(Order):

        @classmethod
        def created_at(cls):
            """Creates and returns an created_at Order
            :return: Order object
            """
            return Order(typ='created_at')

    class Filter(Filter):

        @classmethod
        def by_card_type(cls, card_type):
            """Creates and returns an card_type Filter
            :param str card_type: the card type to filter by
            :return: Filter object
            """
            return Filter('card_type', values=(card_type,), operator=Filter.OPERATOR['EQUAL'])

        @classmethod
        def by_created_at(cls, from_date, to_date=None):
            """Creates and returns an from_date-to_date Filter or from_date Filter for the created_at field
            :param int from_date: the from_date to filter by
            :param int to_date: the to_date to filter by
            :return: Filter object
            """
            return Filter('created_at', values=(from_date, to_date), operator=Filter.OPERATOR['INTERVAL'])

        @classmethod
        def by_type(cls, typ='creditcard'):
            """Creates and returns an from_date-to_date Filter or from_date Filter for the updated_at field
            :param str typ: creditcard or debit
            :return: Filter object
            """
            return Filter('type', values=(typ,), operator=Filter.OPERATOR['EQUAL'])