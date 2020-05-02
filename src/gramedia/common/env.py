"""
Config Helpers
==============

Simple helper-methods meant for parsing application config settings from
environmental variables.  The intention of this module is to make 'config.py'
more readable.
"""
import re
from os import getenv
from functools import partial
from typing import Callable


def __env(app_prefix: str, var_name: str, default: any=None, var_type: Callable[[str], any]=str) -> any:
    """ Fetches an environmental variable and returns it's value as type.
    """
    value = getenv(f'{app_prefix}_{var_name}')

    if value is None:
        return default

    return var_type(value)


_str = partial(__env, var_type=str)


def _bool(app_prefix: str, var_name: str, default: bool=None) -> bool:
    """ Converts an environmental variable to a boolean.
    Accepted truthy values: 1, true, t, y, yes (similar to YAML, with the addition of 1)
    This converter is case-insensitive.
    """
    truthy_values = ['1', 'true', 't', 'y', 'yes', ]
    return __env(app_prefix, var_name, default, lambda x: x.lower() in truthy_values)


def _int(app_prefix: str, var_name: str, default: int=None) -> int:
    """ Converts an environmental variable to an integer.
    """
    return __env(app_prefix, var_name, default, int)


class BadDatabaseUri(Exception):
    pass


def _db_url_to_django(app_prefix: str, var_name: str, default: dict=None):
    """ Converts a database URI string (similar to SQLAlchemy format) to Django.

    **Examples**

    +--------------------------+-----------------------------------------------------------------------+
    | Backend                  | Format                                                                |
    +==========================+=======================================================================+
    | Postgresql/MySQL/Oracle  | {postgresql|mysql|oracle}://{user}:{password}@{host}:{port}/{db_name} |
    | SQlite                   | sqlite3://{absolute_path}                                             |
    +--------------------------+-----------------------------------------------------------------------+
    """
    val = __env(app_prefix, var_name, default, str)

    protocol, rest = re.match(r'^(\w+)://(.*)$', val).groups()
    if not all([protocol, rest]):
        raise BadDatabaseUri()

    if protocol == 'sqlite3':
        regex = re.compile(r'^(?P<NAME>.*)$')
    else:
        regex = re.compile(r'^(?P<USER>\w+?):(?P<PASSWORD>.+)@(?P<HOST>\S+?):(?P<PORT>\d+)/(?P<NAME>\w+)$')

    try:
        rslt = regex.match(rest).groupdict()
        rslt['ENGINE'] = f'django.db.backends.{protocol}'

    except AttributeError:
        raise BadDatabaseUri()

    return rslt


class EnvConfig:
    """ Class that should be used when referencing environmental variables.

    It supports a prefix, so that all environmental variables will automatically be specified
    with some prefix.

    >>> import os
    >>> os.environ.setdefault('GM_DB_PORT', '5432')
    '5432'
    >>> env = EnvConfig('GM')
    >>> env.int('DB_PORT')
    5432

    >>> os.environ.setdefault('GM_DEBUG', 'yes')
    'yes'
    >>> env.boolean('DEBUG')
    True
    """
    def __init__(self, app_prefix: str):
        self.app_prefix = app_prefix

    def boolean(self, var_name: str, default: bool=None) -> bool:
        return _bool(self.app_prefix, var_name, default)

    def string(self, var_name: str, default: str=None) -> str:
        return _str(self.app_prefix, var_name, default)

    def int(self, var_name: str, default: int=None) -> int:
        return _int(self.app_prefix, var_name, default)

    def django_db(self, var_name: str, default: str=None) -> dict:
        return _db_url_to_django(self.app_prefix, var_name, default)
