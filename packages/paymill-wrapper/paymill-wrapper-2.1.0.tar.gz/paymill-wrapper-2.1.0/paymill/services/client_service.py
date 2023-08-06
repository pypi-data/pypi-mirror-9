# coding=utf-8
from ..models.client import Client
from .paymill_service import PaymillService
__author__ = 'yalnazov'


class ClientService(PaymillService):
    def endpoint_path(self):
        return '/clients'

    def paymill_object(self):
        return Client

    def create(self, email=None, description=None):
        """Creates a remote Client object representation with email and/or description
        :param str email: email for client
        :param str description: description for client
        :return Client: the removed Client object
        """
        params = dict(email=email, description=description)
        return self._create(params)

    def detail(self, obj):
        """Returns/refreshes the remote Client representation with that obj.id
        :param Client obj: the Client object with an id set
        :return Client: the fresh Client object
        """
        return self._detail(obj)

    def update(self, obj):
        """Updates and returns a Client object according to its updatable fields
        :param Client obj: the Client object to update
        :return Client: the updated Client object
        """
        return self._update(obj)

    def remove(self, obj):
        """Removes a remote Client representation with that obj.id
        :param Client obj: the Client object with an id set
        :return Client: the removed Client object
        """
        return self._remove(obj)