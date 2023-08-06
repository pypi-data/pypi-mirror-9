# coding=utf-8
__author__ = 'yalnazov'
from jsonobject import *


class Fee(JsonObject):
    type = StringProperty()
    """:type str: Recipient of the fee"""

    application = StringProperty()
    """:type str: If App fee, app object ID (optional)"""

    payment = StringProperty()
    """:type str: Payment object ID from which the fee gets paid"""

    amount = IntegerProperty()
    """:type int: Formatted fee amount"""

    currency = StringProperty()
    """:type str: ISO 4217 formatted currency code"""

    billed_at = IntegerProperty()
    """:type int: Unix-Timestamp for the creation date"""