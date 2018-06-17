"""
Config Helpers
==============

Simple helper-methods meant for parsing application config settings from
environmental variables.  The intention of this module is to make 'config.py'
more readable.
"""
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
