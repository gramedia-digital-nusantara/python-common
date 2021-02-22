from typing import Tuple

from django.conf import settings
from pika import URLParameters
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

from kombu import Connection

_connection = None
_channel = None


def get_publish_connection_and_channel_pika() -> Tuple[BlockingConnection, BlockingChannel]:
    """ Returns a tuple containing the connection and channel to use for this
    application's messages.  It is unnecessary to ever close the connection or the channel,
    and is recommended to keep them alive for as long as the application lives.
    """
    global _channel, _connection
    if not all([_connection, _channel]) or _connection.is_closed:
        url_params = URLParameters(settings.BROKER_URL)
        connection = BlockingConnection(url_params)
        channel = connection.channel()
        _connection = connection
        _channel = channel

    return _connection, _channel


def get_publish_connection_and_channel():
    global _channel, _connection
    if not all([_connection, ]):
        _connection = Connection(settings.BROKER_URL)
        _channel = _connection.channel()

    return _connection, _channel
