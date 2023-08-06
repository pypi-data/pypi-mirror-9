# coding=utf-8
from jsonobject import *
from .order import Order
from .filter import Filter
__author__ = 'yalnazov'


class Webhook(JsonObject):
    id = StringProperty()
    """:type str: Unique identifier of this webhook"""

    url = StringProperty()
    """:type str: the url of the webhook"""

    email = StringProperty()
    """:type str: either the email OR the url have to be set and will be returned"""

    livemode = BooleanProperty()
    """:type boolean: you can create webhooks for livemode and testmode"""

    event_types = ListProperty(StringProperty)
    """:type array of event_types"""

    active = BooleanProperty()
    """:type boolean: if false, no events will be dispatched to this webhook anymore"""

    app_id = StringProperty()
    """:type str or None: App (ID) that created this refund or null if created by yourself."""

    def updatable_fields(self):
        return 'url', 'email', 'active'

    class Order(Order):
        @classmethod
        def url(cls):
            """Creates and returns an url Order
            :return: Order object
            """
            return Order(typ='url')

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

    class Filter(Filter):
        @classmethod
        def by_email(cls, email):
            """Creates and returns an email Filter
            :param str email: the email to filter by
            :return: Filter object
            """
            return Filter('email', values=(email,), operator=Filter.OPERATOR['EQUAL'])

        @classmethod
        def by_url(cls, url):
            """Creates and returns an url Filter
            :param int url: the url to filter by
            :return: Filter object
            """
            return Filter('url', values=(url,), operator=Filter.OPERATOR['EQUAL'])

        @classmethod
        def by_created_at(cls, from_date, to_date=None):
            """Creates and returns an from_date-to_date Filter or from_date Filter for the created_at field
            :param int from_date: the from_date to filter by
            :param int to_date:the to_date to filter by
            :return: Filter object
            """
            return Filter('created_at', values=(from_date, to_date), operator=Filter.OPERATOR['INTERVAL'])