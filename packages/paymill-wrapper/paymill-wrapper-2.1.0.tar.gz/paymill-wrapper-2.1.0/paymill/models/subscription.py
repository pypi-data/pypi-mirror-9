# coding=utf-8
from .order import Order
from .filter import Filter
from . import payment
from . import client
from . import offer
from jsonobject import *
__author__ = 'yalnazov'


class Subscription(JsonObject):

    id = StringProperty()
    """:type str: Unique identifier of this subscription."""

    livemode = BooleanProperty()
    """:type boolean: Whether this subscription was issued while being in live mode or not."""

    offer = ObjectProperty(offer.Offer)
    """:type Offer object"""

    amount = None
    """:type int: the amount of the subscription in cents"""

    temp_amount = StringProperty()#IntegerProperty()
    """":type int or None: a one-time amount in cents, will charge once only"""

    currency = StringProperty()
    """":type str: ISO 4217 formatted currency code"""

    interval = StringProperty()
    """:type str: Defining how often the client should be charged.
       Format: number DAY|WEEK|MONTH|YEAR [, WEEKDAY] Example: 2 DAYS, MONDAY"""

    name = StringProperty()
    """":type str or None: name of the subscription"""

    trial_start = IntegerProperty()
    """:type int or None: Unix-Timestamp for the trial period start"""

    trial_end = IntegerProperty()
    """":type: int or None: Unix-Timestamp for the trial period end"""

    period_of_validity = StringProperty()
    """":type: str or None: limit the validity of the subscription, format: integer MONTH|YEAR|WEEK|DAY"""

    end_of_period = IntegerProperty()
    """":type: int or None: expiring date of the subscription"""

    next_capture_at = IntegerProperty()
    """:type: int: Unix-Timestamp for the next charge."""

    created_at = IntegerProperty()
    """:type: int: Unix-Timestamp for the creation Date."""

    updated_at = IntegerProperty()
    """:type: int: Unix-Timestamp for the last update."""

    canceled_at = IntegerProperty()
    """:type: int: Unix-Timestamp for the cancel date."""

    client = ObjectProperty(client.Client)
    """":type Client:"""

    payment = ObjectProperty(payment.Payment)
    """":type Payment:"""

    app_id = StringProperty()
    """:type string or null: App (ID) that created this payment or null if created by yourself"""

    is_canceled = BooleanProperty()
    """:type boolean: subscription is marked as canceled or not"""

    is_deleted = BooleanProperty()
    """:type boolean: subscription is marked as deleted or not"""

    status = StringProperty()
    """:type str: shows, if subscription is active, inactive, expired or failed"""

    def updatable_fields(self):
        return 'payment', 'currency', 'interval', 'name', 'period_of_validity', 'trial_end'

    #workaround for returned type of amount
    def __getattribute__(self, name):
        if name == 'amount':
            attr = object.__getattribute__(self, name)
            return int(attr)
        return object.__getattribute__(self, name)

    class Order(Order):
        @classmethod
        def offer(cls):
            """Creates and returns an offer Order
            :return: Order object
            """
            return Order(typ='offer')

        @classmethod
        def canceled_at(cls):
            """Creates and returns an canceled_at Order
            :return: Order object
            """
            return Order(typ='canceled_at')

        @classmethod
        def created_at(cls):
            """Creates and returns an created_at Order
            :return: Order object
            """
            return Order(typ='created_at')

    class Filter(Filter):

        @classmethod
        def by_offer_id(cls, offer_id):
            """Creates and returns an offer_id Filter
            :param str offer_id: the offer id to filter by
            :return: Filter object
            """
            return Filter('offer', values=(offer_id,), operator=Filter.OPERATOR['EQUAL'])

        @classmethod
        def by_created_at(cls, from_date, to_date=None):
            """Creates and returns an from_date-to_date Filter or from_date Filter for the created_at field
            :param int from_date: the from_date to filter by
            :param int to_date:the to_date to filter by
            :return: Filter object
            """
            return Filter('created_at', values=(from_date, to_date), operator=Filter.OPERATOR['INTERVAL'])