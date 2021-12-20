from django.conf import settings
from kombu import Connection

_connection = None
_channel = None


def get_publish_connection_and_channel():
    global _channel, _connection
    if not all([_connection, ]):
        _connection = Connection(settings.BROKER_URL)
        _channel = _connection.channel()

    return _connection, _channel
