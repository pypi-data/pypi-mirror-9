# coding=utf-8
from ..models.webhook import Webhook
from .paymill_service import PaymillService
from json import dumps
__author__ = 'yalnazov'


class WebhookService(PaymillService):
    def endpoint_path(self):
        return '/webhooks'

    def paymill_object(self):
        return Webhook

    def create_url(self, url, event_types, active):
        """Creates a remote URL Webhook object representation
        :param str url: the url of the webhook
        :param list event_types: includes a set of webhook event types as strings
        :param boolean active: can be used to create an inactive webhook in the beginning
        :return Webhook: the created Webhook object:
        """
        params = dict(url=url, active=dumps(active), **WebhookService._event_types_to_dict(event_types))
        return self._create(params)

    def create_email(self, email, event_types, active):
        """Creates a remote URL Webhook object representation
        :param str email: the webhooks email. must be a valid mail address
        :param list event_types: includes a set of webhook event types as strings
        :param boolean active: can be used to create an inactive webhook in the beginning
        :return Webhook: the created Webhook object:
        """
        params = dict(email=email, active=dumps(active), **WebhookService._event_types_to_dict(event_types))
        return self._create(params)

    @classmethod
    def _event_types_to_dict(cls, event_types):
        event_types_dict = {}
        for e in event_types:
            event_types_dict.update(dict({'event_types[]': e}))
        return event_types_dict

    def detail(self, obj):
        """Returns/refreshes the remote Webhook representation with that obj.id
        :param Webhook obj: the Webhook object with an id set
        :return Webhook: the fresh Webhook object:
        """
        return self._detail(obj)

    def update(self, obj):
        """Updates and returns a Webhook object according to its updatable fields
        :param Webhook obj: the Webhook object to update
        :return Webhook: the updated Webhook object
        """
        return self._update(obj, **WebhookService._event_types_to_dict(obj.event_types))

    def remove(self, obj):
        """Removes a remote Webhook representation with that obj.id
        :param Webhook obj: the Webhook object with an id set
        :return Webhook: the removed Webhook object:
        """
        return self._remove(obj)