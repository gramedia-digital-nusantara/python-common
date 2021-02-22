import logging
from enum import Enum

from typing import Type

import msgpack
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.timezone import now
from pika import BlockingConnection, exceptions
from pika.adapters.blocking_connection import BlockingChannel
from kombu import Connection, producers, Exchange
from rest_framework.serializers import BaseSerializer

from .amqp_connection import get_publish_connection_and_channel

_logger = logging.getLogger(__name__)


class EventType(Enum):
    created = 'created'
    changed = 'changed'
    deleted = 'deleted'
    deactivated = 'deactivated'
    activated = 'activated'


class BasicPublisher:
    """ Object used for publishing.
    """

    def __init__(self,
                 exchange_name: str,
                 site: Site,
                 connection: BlockingConnection = None,
                 channel: BlockingChannel = None):
        """ Creates a new instance of BasicPublisher.
        If connection or channel are not defined, they will be initialized
        automatically from the global publish connection and channel objects.

        :param exchange_name:  Name of the exchange this publisher should publish to.
        :param connection: (optional) AMQP connection object.
        :param channel: (optional) AMQP channel that will be used to publish messages.
        """
        self.exchange_name = exchange_name
        self.site = site

        if not all([connection, channel]):
            self._connection, self._channel = get_publish_connection_and_channel()
        else:
            self._connection = connection
            self._channel = channel

    def create_exchange(self, exchange_type='topic') -> None:
        """ Creates an exchange
        """
        if self._channel.is_closed:
            self._connection, self._channel = get_publish_connection_and_channel()
        self._channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type=exchange_type,
            durable=True
        )

    def get_identity(self, data: dict) -> str:
        return data['href']

    def simulate_context(self) -> dict:
        """ Simulates a request context sot hat our serializers can operate properly.

        :param site_id: Optional parameter (but should geenrally
        :return: A single-key dictionary containing 'request' with a simulated request object.
        """
        # this is a terrible hack to make the requests still work from the CLI.
        from rest_framework.request import Request, HttpRequest

        class SimulatedHTTPRequest(HttpRequest):
            def _get_scheme(self):
                return "https"

        req = SimulatedHTTPRequest()

        req.META = {
            'SERVER_NAME': self.site.domain,
            'SERVER_PORT': 443,
            'SCRIPT_NAME': settings.FORCE_SCRIPT_NAME
        }
        return {'request': Request(req)}

    def construct_message(self, data: dict, entity_type: str, event_type: EventType, identity=None) -> bytes:
        """ Construct the message to be sent.
        """
        message = {
            "event_time": now().isoformat(),
            "identity": identity or self.get_identity(data),
            "event_type": event_type.value,
            "entity_type": entity_type,
            "entity_site": self.site.domain,
            "data": data
        }
        return msgpack.packb(message, use_bin_type=True)

    def publish(self,
                message: any,
                message_serializer: Type[BaseSerializer],
                event_type: EventType,
                entity_type: str,
                message_identity: any = None) -> None:
        """ Publish the message to RabbitMQ.
        """
        data = message_serializer(message, context=self.simulate_context()).data

        body = self.construct_message(
            data=data,
            entity_type=entity_type,
            event_type=event_type,
            identity=message_identity
        )

        # is_message_success_send = False
        # connection = Connection(settings.BROKER_URL)
        with producers[self._connection].acquire(block=True, timeout=60) as producer:
            the_exchange = Exchange(name=self.exchange_name, type='topic', durable=True, channel=self._channel)
            try:
                _logger.info(f'QUEUE Publish {self.site.domain}-{entity_type}:{event_type} - {data} ')
                producer.publish(
                    body=body,
                    exchange=the_exchange,
                    routing_key=event_type.value,
                    declare=[the_exchange],
                    serializer='msgpack',
                    retry=True,
                    retry_policy={
                        'interval_start': 0,  # First retry immediately,
                        'interval_step': 2,   # then increase by 2s for every retry.
                        'interval_max': 30,   # but don't exceed 30s between retries.
                        'max_retries': 30,    # give up after 30 tries.
                    },
                )
            except exceptions.AMQPConnectionError as exc:
                _logger.exception(f"AMQP error - reconnecting attempt ({exc}) ")

class BasicConsumer:
    def __init__(self,
                 exchange_name: str,
                 queue_name: str,
                 routing_key: str,
                 connection: BlockingConnection = None,
                 channel: BlockingChannel = None):

        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_key = routing_key

        if not all([connection, channel]):
            self._connection, self._channel = get_publish_connection_and_channel()
        else:
            self._connection = connection
            self._channel = channel

    def create_exchange(self, exchange_type='topic') -> None:
        self._channel.exchange_declare(exchange=self.exchange_name,
                                       exchange_type=exchange_type,
                                       durable=True)

    def create_queue(self):
        self._channel.queue_declare(queue=self.queue_name)
        self._channel.queue_bind(queue=self.queue_name,
                                 exchange=self.exchange_name,
                                 routing_key=self.routing_key
                                 )


M2M_PRE_REMOVE = 'pre_remove'
M2M_POST_REMOVE = 'post_remove'
