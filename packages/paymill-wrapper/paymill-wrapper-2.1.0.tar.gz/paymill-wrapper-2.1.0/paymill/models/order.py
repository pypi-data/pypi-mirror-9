# coding=utf-8
__author__ = 'yalnazov'


class Order(object):

    def __init__(self, typ):
        if typ is None:
            raise ValueError('None pass for order typ!')
        self.typ = typ
        self.ascending = None

    def asc(self):
        self.ascending = True
        return self

    def desc(self):
        self.ascending = False
        return self

    def to_dict(self):
        result = self.typ
        if self.ascending:
            result += '_asc'
        else:
            result += '_desc'

        return dict(order=result)

