import logging
import os
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

from gramedia.django.signalling import EventType

_logger = logging.getLogger('LOG')
_logger_audit = logging.getLogger('AUDIT')

UserModel = get_user_model()

_LOGGER_KEY = 'SECAGUSER'

__ALL__ = ['process_security_auth_group_message', ]


def process_security_auth_group_message(message):
    _logger.info(f'[*] {_LOGGER_KEY} Consuming Security Auth Group - User queue')
    event_type = message.get('event_type', '')
    entity = message.get('data')

    identity_parts = urlparse(message.get('identity'))
    site = Site.objects.get(domain=message.get('entity_site') or identity_parts.hostname)
    customer_identity_parts = urlparse(message.get('customer'))
    customer_identity = os.path.basename(os.path.normpath(identity_parts.path))
    try:
        user = get_user_model().objects.filter(username=customer_identity).first()
        if not user:
            raise UserModel.DoesNotExist

        access_group = Group.objects.get(id=entity.get('access_group'))
    except Group.DoesNotExist as exc:
        _logger.exception(f'{_LOGGER_KEY} not find access group {entity.get("access_group")}')
        raise
    except UserModel.DoesNotExist:
        _logger.exception(f'{_LOGGER_KEY} not find user {entity.get("customer")}')
        raise

    _logger.info(f"{_LOGGER_KEY} Receive business {message}")
    if user and access_group:
        if event_type == EventType.assigned.value:
            access_group.user_set.add(user)
        elif event_type == EventType.revoked.value:
            access_group.user_set.remove(user)
        else:
            _logger.error(f'{_LOGGER_KEY} Cannot match the event {event_type}')
    else:
        _logger.error(f'{_LOGGER_KEY} Cannot match the user or auth group')
