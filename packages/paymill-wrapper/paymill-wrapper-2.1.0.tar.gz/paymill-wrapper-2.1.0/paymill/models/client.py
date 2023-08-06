# coding=utf-8
from .order import Order
from .filter import Filter
from jsonobject import *
__author__ = 'yalnazov'


class Client(JsonObject):

    id = StringProperty()
    """:type str: Unique identifier of this client"""

    email = StringProperty()
    """:type str or None: Mail address of this client."""

    description = StringProperty()
    """:type str or None: Additional description for this client, perhaps the identifier from your CRM system?"""

    payment = None
    """:type <Payment>: list of cc or debit objects"""

    subscription = None
    """:type list or null: subscription object (optional)"""

    created_at = IntegerProperty()
    """:type integer: unix timestamp identifying time of creation"""

    updated_at = IntegerProperty()
    """:type integer. unix timestamp identifying time of last change"""

    app_id = StringProperty()
    """:type string or null. App (ID) that created this payment or null if created by yourself"""

    #dynamic JSON to Python representation to resolve circular dependencies between client, payment and subscription
    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if name == 'subscription':
            from . import subscription
            return ListProperty(subscription.Subscription).wrap(attr)
        if name == 'payment':
            from . import payment
            if isinstance(attr, dict):
                return ListProperty(payment.Payment).wrap(attr)
            if isinstance(attr, str):
                return list(payment.Payment(id=attr))

        return object.__getattribute__(self, name)

    def updatable_fields(self):
        return 'email', 'description'

    class Order(Order):
        @classmethod
        def email(cls):
            """Creates and returns an email Order
            :return: Order object
            """
            return Order(typ='email')

        @classmethod
        def created_at(cls):
            """Creates and returns an created_at Order
            :return: Order object
            """
            return Order(typ='created_at')

        @classmethod
        def creditcard(cls):
            """Creates and returns an creidtcard Order
            :return: Order object
            """
            return Order(typ='creditcard')

    class Filter(Filter):

        @classmethod
        def by_payment_id(cls, payment_id):
            """Creates and returns an payment_id Filter
            :param str payment_id: the payment id to filter by
            :return: Filter object
            """
            return Filter('payment', values=(payment_id,), operator=Filter.OPERATOR['EQUAL'])

        @classmethod
        def by_subscription_id(cls, subscription_id):
            """Creates and returns an subscription_id Filter
            :param str subscription_id: the subscription id to filter by
            :return: Filter object
            """
            return Filter('subscription', values=(subscription_id,), operator=Filter.OPERATOR['EQUAL'])

        @classmethod
        def by_offer_id(cls, offer_id):
            """Creates and returns an offer_id Filter
            :param str offer_id: the offer id to filter by
            :return: Filter object
            """
            return Filter('offer', values=(offer_id,), operator=Filter.OPERATOR['EQUAL'])

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
            return Filter('created_at', values=(from_date, to_date), operator=Filter.OPERATOR['EQUAL'])



        @classmethod
        def by_updated_at(cls, from_date, to_date=None):
            """Creates and returns an from_date-to_date Filter or from_date Filter for the updated_at field
            :param int from_date: the from_date to filter by
            :param int to_date:the to_date to filter by
            :return: Filter object
            """
            return Filter('updated_at', values=(from_date, to_date), operator=Filter.OPERATOR['INTERVAL'])