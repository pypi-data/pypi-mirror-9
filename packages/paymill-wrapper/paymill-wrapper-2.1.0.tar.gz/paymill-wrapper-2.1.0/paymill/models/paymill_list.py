# coding=utf-8
__author__ = 'yalnazov'
from jsonobject import *


class PaymillList(JsonObject):
        data = ListProperty()
        mode = StringProperty()
        data_count = StringProperty()
