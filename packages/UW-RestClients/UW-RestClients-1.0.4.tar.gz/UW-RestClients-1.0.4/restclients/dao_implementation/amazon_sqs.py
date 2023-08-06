"""
Contains Amazon SWS DAO implementations.
"""
from restclients.models import MockAmazonSQSQueue
from boto.sqs.connection import SQSConnection
from boto.sqs.message import RawMessage
from django.db import IntegrityError
from django.conf import settings


class Local(object):
    """
    This implements a local queue, using django models.
    """
    def create_queue(self, queue_name):
        obj, created = MockAmazonSQSQueue.objects.get_or_create(name=queue_name)

        return obj

    def get_queue(self, queue_name):
        queues = MockAmazonSQSQueue.objects.filter(name=queue_name)
        if len(queues):
            return queues[0]

        return None


class Live(object):
    """
    This implements a connection to the Amazon SQS service.  Requires the
    following configuration:

    RESTCLIENTS_AMAZON_AWS_ACCESS_KEY
    RESTCLIENTS_AMAZON_AWS_SECRET_KEY
    """

    def create_queue(self, queue_name):
        conn = self._get_connection()
        return conn.create_queue(queue_name)

    def get_queue(self, queue_name):
        conn = self._get_connection()
        queue = conn.get_queue(queue_name)
        queue.set_message_class(RawMessage)
        return queue

    def _get_connection(self):
        access_key = settings.RESTCLIENTS_AMAZON_AWS_ACCESS_KEY
        secret_key = settings.RESTCLIENTS_AMAZON_AWS_SECRET_KEY

        conn = SQSConnection(access_key, secret_key)
        return conn
