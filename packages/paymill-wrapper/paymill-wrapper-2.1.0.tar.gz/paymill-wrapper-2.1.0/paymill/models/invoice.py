# coding=utf-8
__author__ = 'yalnazov'
from jsonobject import *


class Invoice(JsonObject):
    invoice_nr = StringProperty()
    """:type str: invoice number"""

    netto = IntegerProperty()
    """:type int: Formatted netto amount"""

    brutto = IntegerProperty()
    """:type int: Formatted brutto amount"""

    status = StringProperty()
    """:type str: Invoice status (e.g. sent, trx_ok, trx_failed, invalid_payment,
       success, 1st_reminder, 2nd_reminder, 3rd_reminder, suspend, canceled, transferred)"""

    period_from = IntegerProperty()
    """:type int: Unix-Timestamp for the start of this invoice period"""

    period_until = IntegerProperty()
    """:type int: Unix-Timestamp for the end of this invoice period"""

    currency = StringProperty()
    """"":type str: ISO 4217 formatted currency code."""

    vat_rate = IntegerProperty()
    """":type int: VAT rate of the brutto amount"""

    billing_date = IntegerProperty()
    """:type int: Unix-Timestamp for the billing date"""

    invoice_type = StringProperty()
    """:type str: enum(paymill, wirecard, acceptance etc.)
       Indicates if it”s a PAYMILL invoice or an acquirer payout."""

    last_reminder = IntegerProperty()
    """:type int: Unix-Timestamp for last payment reminder"""



