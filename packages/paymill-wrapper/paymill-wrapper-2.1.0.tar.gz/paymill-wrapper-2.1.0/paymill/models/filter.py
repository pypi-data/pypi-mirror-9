# coding=utf-8
__author__ = 'yalnazov'
from six import text_type


class Filter(object):

    class IllegalOperator(Exception):
        pass

    OPERATOR = dict(LESS_THAN="<",
                    GREATER_THAN=">",
                    EQUAL="",
                    INTERVAL="-")

    def __init__(self, key, values=tuple(), operator=OPERATOR['EQUAL']):
        if key is None:
            raise ValueError('None passed for key to Filter!')

        if values[0] is None:
            raise ValueError('None passed for value to Filter!')

        self.key = str(key)
        self.values = values
        if not operator in self.OPERATOR.values():
            raise self.IllegalOperator(u"illegal operator %s" % text_type(operator))
        self.operator = operator

        if len(self.values) > 1 and self.values[1] is None:
            self.operator = Filter.OPERATOR['EQUAL']
        elif len(self.values) > 1:
            self.operator = Filter.OPERATOR['INTERVAL']

    def to_dict(self):
        result = str(self.values[0]) + self.operator
        if len(self.values) > 1 and self.values[1] is not None:
            result += str(self.values[1])
        return dict([(self.key, result)])

    def __eq__(self, other):
        if not isinstance(other, Filter):
            return False
        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return str(self.to_dict())


class FilterList(Filter):

    def __init__(self, *filters):
        self.filters = filters

    def to_dict(self):
        combined_dict = dict()
        for filtr in self.filters:
            combined_dict.update(filtr.to_dict())
        return combined_dict
