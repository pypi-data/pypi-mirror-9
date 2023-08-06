# coding=utf-8
__author__ = 'yalnazov'
from paymill.models.filter import Filter
from paymill.models.order import Order
from jsonobject import *


class SubscriptionCount(JsonObject):
    active = None
    inactive = None


class Offer(JsonObject):
    id = StringProperty()
    """:type str: Unique identifier of this offer"""

    name = StringProperty()
    """:type str: Your name for this offer"""

    amount = None
    """:type int (>0): Every interval the specified amount will be charged.
       Only integer values are allowed (e.g. 42.00 = 4200)"""

    interval = StringProperty()
    """:type str: Defining how often the client should be charged.
       Format: number DAY | WEEK | MONTH | YEAR Example: 2 DAY"""

    currency = StringProperty()
    """:type str: ISO 4217 formatted currency code."""

    trial_period_days = IntegerProperty()
    """:type int or None: Define an optional trial period in number of days"""

    created_at = IntegerProperty()
    """:type int: Unix-Timestamp for the creation Date"""

    updated_at = IntegerProperty()
    """:type int: Unix-Timestamp for the last update"""

    subscription_count = ObjectProperty(SubscriptionCount)
    """:type int (>0):Attributes: (integer) if zero, else (string) active, (integer) if zero, else (string) inactive"""

    app_id = StringProperty()
    """:type str or None: App (ID) that created this offer or null if created by yourself."""

    def updatable_fields(self):
        return 'name', 'interval', 'amount', 'currency', 'trial_period_days'

    class Order(Order):
        @classmethod
        def interval(cls):
            """Creates and returns an interval Order
            :return: Order object
            """
            return Order(typ='interval')

        @classmethod
        def created_at(cls):
            """Creates and returns an created_at Order
            :return: Order object
            """
            return Order(typ='created_at')

        @classmethod
        def amount(cls):
            """Creates and returns an amount Order
            :return: Order object
            """
            return Order(typ='amount')

        @classmethod
        def trial_period_days(cls):
            """Creates and returns an trial_period_days Order
            :return: Order object
            """
            return Order(typ='trial_period_days')

    class Filter(Filter):

        @classmethod
        def by_name(cls, name):
            """Creates and returns an name Filter
            :param str name: the payment id to filter by
            :return: Filter object
            """
            return Filter('payment', values=(name,), operator=Filter.OPERATOR['EQUAL'])

        @classmethod
        def by_trial_period_days(cls, trial_period_days):
            """Creates and returns an trial_period_days Filter
            :param int trial_period_days: the trial_period_days to filter by
            :return: Filter object
            """
            return Filter('trial_period_days', values=(trial_period_days,), operator=Filter.OPERATOR['EQUAL'])

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

        @classmethod
        def by_updated_at(cls, from_date, to_date=None):
            """Creates and returns an from_date-to_date Filter or from_date Filter for the updated_at field
            :param int from_date: the from_date to filter by
            :param int to_date:the to_date to filter by
            :return: Filter object
            """
            return Filter('updated_at', values=(from_date, to_date), operator=Filter.OPERATOR['INTERVAL'])
