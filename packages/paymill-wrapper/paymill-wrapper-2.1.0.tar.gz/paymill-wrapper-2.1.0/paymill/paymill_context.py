# coding=utf-8
__author__ = 'yalnazov'
from .utils import http_client
from .services import client_service
from .services import offer_service
from .services import payment_service
from .services import preauthorization_service
from .services import refund_service
from .services import subscription_service
from .services import transaction_service
from .services import webhook_service


class PaymillContext(object):

    """Entry point for PAYMILL API.
       Use the getter methods in order to access the required PAYMILL service.
    """

    def __init__(self, api_key):
        """
        :param str api_key: your PAYMILL private key
        :rtype : PaymillContext
        """
        self.api_url = 'https://api.paymill.com/v2.1'
        self.api_key = api_key
        self.http_client = http_client.HTTPClient(self.api_url, api_key, "")
        self.client_service = client_service.ClientService(self.http_client)
        self.offer_service = offer_service.OfferService(self.http_client)
        self.payment_service = payment_service.PaymentService(self.http_client)
        self.preauthorization_service = preauthorization_service.PreauthorizationService(self.http_client)
        self.refund_service = refund_service.RefundService(self.http_client)
        self.subscription_service = subscription_service.SubscriptionService(self.http_client)
        self.transaction_service = transaction_service.TransactionService(self.http_client)
        self.webhook_service = webhook_service.WebhookService(self.http_client)

    """Getter methods for each PAYMILL service."""

    def get_client_service(self):
        return self.client_service

    def get_offer_service(self):
        return self.offer_service

    def get_payment_service(self):
        return self.payment_service

    def get_preauthorization_service(self):
        return self.preauthorization_service

    def get_refund_service(self):
        return self.refund_service

    def get_subscription_service(self):
        return self.subscription_service

    def get_transaction_service(self):
        return self.transaction_service

    def get_webhook_service(self):
        return self.webhook_service