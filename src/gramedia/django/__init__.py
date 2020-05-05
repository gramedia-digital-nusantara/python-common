from logging import getLogger

log = getLogger('gramedia')

try:
    import django
    import rest_framework
except ModuleNotFoundError:
    log.exception('This module requires django and rest_framework')
    raise
