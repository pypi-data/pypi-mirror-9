# coding=utf-8
from ..models.subscription import Subscription
from .paymill_service import PaymillService

__author__ = 'yalnazov'


class SubscriptionService(PaymillService):
    def endpoint_path(self):
        return '/subscriptions'

    def paymill_object(self):
        return Subscription

    def create_with_amount(self, payment_id, amount, currency, interval, client_id=None, name=None, period_of_validity=None,
                           start_at=None):
        """Creates a remote Subscription object representation
        :param str payment_id: A token generated through our JavaScript-Bridge
        :param int amount: Amount (in cents) which will be charged
        :param str currency: ISO 4217 formatted currency code
        :param str interval: Defining how often the client should be charged.
               Format: number DAY|WEEK|MONTH|YEAR [, WEEKDAY] Example: 2 DAYS, MONDAY
        :param str client_id or None: The identifier of a client
        :param str name or None: name of the subscription (optional)
        :param str or None period_of_validity : limit the validity of the subscription,
               format: integer MONTH|YEAR|WEEK|DAY
        :param int or None start_at : Unix-Timestamp for the subscription start date,
               if trial_end > start_at, the trial_end will be set to start_at
        :return Subscription: the created Subscription object
        """

        return self._create_subscription(dict(client=client_id, name=name,
                                              period_of_validity=period_of_validity,
                                              start_at=start_at),
                                         payment_id, None, amount, currency, interval)

    def create_with_offer_id(self, payment_id, offer_id, client_id=None, name=None, period_of_validity=None,
                             start_at=None):
        """Creates a remote Subscription object representation
        :param str payment_id: A token generated through our JavaScript-Bridge
        :param int offer_id: Unique offer identifier
               Format: number DAY|WEEK|MONTH|YEAR [, WEEKDAY] Example: 2 DAYS, MONDAY
        :param str client_id or None: The identifier of a client
        :param str name or None: name of the subscription (optional)
        :param str or None period_of_validity : limit the validity of the subscription,
               format: integer MONTH|YEAR|WEEK|DAY
        :param int or None start_at : Unix-Timestamp for the subscription start date,
               if trial_end > start_at, the trial_end will be set to start_at
        :return Subscription: the created Subscription object
        """
        if payment_id is None:
            raise ValueError('Payment id is None!')

        return self._create_subscription(dict(client=client_id, name=name,
                                              period_of_validity=period_of_validity,
                                              start_at=start_at),
                                         payment_id, offer_id, None, None, None)

    def _create_subscription(self, params, payment_id, offer_id, amount, currency, interval):
        if payment_id is None:
            raise ValueError('Payment id is None!')

        if offer_id is None and (amount is None or currency is None or interval is None):
            raise ValueError('Either an offer or amount, currency and interval must be set, '
                             'when creating a subscription!')

        params.update(payment=payment_id, offer=offer_id, amount=amount, currency=currency, interval=interval)

        return self._create(params)

    def detail(self, obj):
        """Returns/refreshes the remote Subscription representation with that obj.id
        :param Subscription obj: the Subscription object with an id set
        :return Subscription: the fresh Subscription object
        """
        return self._detail(obj)

    def update(self, obj):
        """Updates and returns a Subscription object according to its updatable fields
           In order to update offer or amount, please use the specific methods below.
        :param Subscription obj: the Subscription object to update
        :return Subscription: the updated Subscription object
        """
        return self._update(obj)

    def update_with_offer_id(self, obj, offer_change_type):
        """Updates and returns a Subscription object with offer
        :param Subscription obj: the Subscription object to update
        :param int or None offer_change_type: permitted values: 0,1,2;
        :return Subscription: the updated Subscription object
        """
        if obj.payment is None or obj.offer is None or offer_change_type is None:
            raise ValueError('Payment, Offer or Offer Change Type None!')
        return self._update(obj, **dict(payment=obj.payment.id, offer=obj.offer.id, offer_change_type=offer_change_type))

    def update_with_amount(self, obj, amount_change_type):
        """Updates and returns a Subscription object with amount
        :param Subscription obj: the Subscription object to update
        :param int or None amount_change_type: permitted values: 0,1,2;
        :return Subscription: the updated Subscription object
        """
        if obj.amount is None and amount_change_type is None:
            raise ValueError('Amount or Amount Change Type None!')
        return self._update(obj, **dict(amount=obj.amount, amount_change_type=amount_change_type))

    def pause(self, obj):
        """Updates and returns a Subscription object and
           PAUSES it
        :param Subscription obj: the Subscription object to update
        :param int or None amount_change_type: permitted values: 0,1,2;
        :return Subscription: the updated Subscription object
        """
        self._update(obj, **dict(pause=True))

    def unpause(self, obj):
        """Updates and returns a Subscription object and
        UNPAUSES it
        :param Subscription obj: the Subscription object to update
        :param int or None amount_change_type: permitted values: 0,1,2;
        :return Subscription: the updated Subscription object
        """
        self._update(obj, **dict(pause=False))

    def remove(self, obj):
        """Removes a remote Subscription representation with that obj.id
        :param Subscription obj: the Subscription object with an id set
        :return Subscription: the removed Subscription object
        """
        return self._remove(obj, dict(remove='true'))

    def cancel(self, obj):
        """Cancels a remote Subscription representation with that obj.id
        :param Subscription obj: the Subscription object with an id set
        :return Subscription: the removed Subscription object
        """
        return self._remove(obj, dict(remove='false'))