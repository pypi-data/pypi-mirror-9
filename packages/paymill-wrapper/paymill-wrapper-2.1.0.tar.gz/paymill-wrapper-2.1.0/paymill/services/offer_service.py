# coding=utf-8
from ..models.offer import Offer
from .paymill_service import PaymillService
__author__ = 'yalnazov'


class OfferService(PaymillService):
    def endpoint_path(self):
        return '/offers'

    def paymill_object(self):
        return Offer

    def create(self, amount, currency, interval, name, trial_period_days=None):
        """Creates a remote Offer object representation
        :param int(>0) amount: Amount (in cents)
        :param str currency: ISO 4217 formatted currency code
        :param str interval: Defining how often the client should be charged.
               Format: number DAY|WEEK|MONTH|YEAR Example: 2 DAY
        :param str name: Your name for this offer.
        :param int trial_period_days: Define an optional trial period in number of days
        :return Offer: the removed Offer object
        """
        params = dict(amount=amount, currency=currency, interval=interval,
                      name=name, trial_period_days=trial_period_days)
        return self._create(params)

    def detail(self, obj):
        """Returns/refreshes the remote Offer representation with that obj.id
        :param Offer obj: the Offer object with an id set
        :return Offer: the fresh Offer object
        """
        return self._detail(obj)

    def update(self, obj, update_subscriptions=False):
        """Updates and returns an Offer object according to its updatable fields
        :param Offer obj: the Offer object to update.
        :param boolean update_subscriptions: Definition, if all related subscriptions also should be updated.
        :return Offer: the updated Offer object
        """
        return self._update(obj, **dict(update_subscriptions=update_subscriptions))

    def remove(self, obj, remove_with_subscriptions='false'):
        """Removes a remote Offer representation with that obj.id
        :param Offer obj: the Offer object with an id set
        :param boolean remove_with_subscriptions: Definition if all related subscriptions also should be deleted.
        :return Offer: the removed Offer object
        """
        return self._remove(obj, params=dict(remove_with_subscriptions=remove_with_subscriptions))