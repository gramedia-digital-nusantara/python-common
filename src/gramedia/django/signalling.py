import logging
import time
from enum import Enum
from typing import Type

import msgpack
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.timezone import now
from kombu import Exchange, producers, Connection, Consumer, Producer, uuid, Queue
from rest_framework.serializers import BaseSerializer

from gramedia.django.amqp_connection import get_publish_connection_and_channel

_logger = logging.getLogger('LOG')
_logger_audit = logging.getLogger('AUDIT')

User = get_user_model()


class EventType(Enum):
    created = 'created'
    changed = 'changed'
    deleted = 'deleted'
    deactivated = 'deactivated'
    activated = 'activated'
    assigned = 'assigned'
    revoked = 'revoked'


class BasicPublisher:
    """ Object used for publishing.
    """

    def __init__(self,
                 exchange_name: str,
                 site: Site,
                 connection: Connection = None,
                 channel=None):
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
        if not self._channel.is_open:
            self._connection, self._channel = get_publish_connection_and_channel()
        self._channel.exchange_declare(
            exchange=self.exchange_name,
            type=exchange_type,
            durable=True,
            auto_delete=False
        )

    def get_identity(self, data: dict) -> str:
        return data['href']

    def get_user_href(self, user: User) -> str:
        if isinstance(user, str):
            return user
        return f'https://{self.site.domain}/api/iam/user/{user.username}/' if user else ''

    def simulate_context(self) -> dict:
        """ Simulates a request context sot hat our serializers can operate properly.

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

    def construct_message(self, data: dict, entity_type: str, event_type: EventType, identity: object = None, user: object = None) -> bytes:
        """ Construct the message to be sent.
        :param data: A dictionary of data to be sent
        :param entity_type: Name of the entity
        :param event_type: Event type
        :param identity: Message identifier
        :param user: User that does the event
        :return: A message pack encoded data
        """
        message = {
            "event_time": now().isoformat(),
            "identity": identity or self.get_identity(data),
            "event_type":  event_type.value,
            "entity_type": entity_type,
            "entity_site": self.site.domain,
            "user": self.get_user_href(user) if user else '',
            "data": data
        }
        return msgpack.packb(message, use_bin_type=True)

    def publish(self,
                message: any,
                message_serializer: Type[BaseSerializer],
                event_type: EventType,
                entity_type: str,
                message_identity: any = None,
                user: User = None) -> None:
        """ Publish the message to RabbitMQ.
        :param message:
        :param message_serializer:
        :param event_type:
        :param entity_type:
        :param message_identity:
        :param user:
        """
        self.create_exchange()
        if message_serializer is not None:
            data = message_serializer(message, context=self.simulate_context()).data
        else:
            if type(message) == dict:
                data = message
            else:
                data = {}

        body = self.construct_message(
            data=data,
            entity_type=entity_type,
            event_type=event_type,
            identity=message_identity,
            user=user
        )

        with producers[self._connection].acquire(block=True, timeout=60) as producer:
            the_exchange = Exchange(name=self.exchange_name, type='topic', durable=True, channel=self._channel)
            try:
                _logger.info(f'QUEUE Publish {self.site.domain}-{entity_type}:{event_type} - {data} ')
                producer.publish(
                    body=body,
                    exchange=the_exchange,
                    routing_key=f'{entity_type}.{event_type.value}',
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
            except Exception as exc:
                _logger.exception(f"AMQP error - reconnecting attempt ({exc}) ")


class BasicRpcClient:

    def __init__(self, routing):
        self.connection, self.channel = get_publish_connection_and_channel()
        self.callback_queue = Queue(uuid(), exclusive=True, auto_delete=True)
        self.response = None
        self.routing_key = routing

    def on_response(self, message):
        if message.properties['correlation_id'] == self.correlation_id:
            import msgpack
            self.response = msgpack.unpackb(message.body).get('result')

    def call(self, message: dict, event_type: str, entity_type: str, site: Site) -> any:
        self.response = None
        self.correlation_id = uuid()
        with Producer(self.connection) as producer:
            _logger.info(f'CELERY RPC call {site.domain} with {event_type} - {entity_type} {message} reply to {self.correlation_id}')
            producer.publish(
                {
                    "event_type": event_type,
                    "entity_type": entity_type,
                    "entity_site": site.domain,
                    "data": message
                },
                exchange='',
                routing_key=self.routing_key,
                declare=[self.callback_queue],
                reply_to=self.callback_queue.name,
                correlation_id=self.correlation_id,
                serializer='msgpack',
            )

        with Consumer(self.connection,
                      on_message=self.on_response,
                      queues=[self.callback_queue], no_ack=True):
            _logger.info(f'CELERY RPC call consume {site.domain} with {event_type} - {entity_type} {message} reply to {self.correlation_id}')
            t_current = time.time()
            while self.response is None:
                self.connection.drain_events(timeout=1)
                # time.sleep(0.25)  # sleep for 250 milliseconds
                # if time.time() >= t_current + 60000:
                #     break
        _logger.info(f'CELERY RPC call consume {site.domain} with response {self.response}')

        return self.response
