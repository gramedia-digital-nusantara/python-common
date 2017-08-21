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


def __env(app_prefix: str, varname: str, default: any=None, type: Callable[[str], any]=str) -> any:
    """ Fetches an environmental variable and returns it's value as type.
    """
    value = getenv(f'{app_prefix}_{varname}')

    if value is None:
        return default

    return type(value)


_str = partial(__env, type=str)


def _bool(app_prefix: str, varname: str, default: bool=None) -> bool:
    return __env(app_prefix, varname, default, lambda x: x.lower() in ['1', 'true', 't'])


def _int(app_prefix: str, varname: str, default: int=None) -> int:
    return __env(app_prefix, varname, default, int)


class EnvConfig:

    def __init__(self, app_prefix: str):
        self.app_prefix = app_prefix

    def boolean(self, varname: str, default: str=None) -> bool:
        return _bool(self.app_prefix, varname, default)

    def string(self, varname: str, default: str=None) -> str:
        return _str(self.app_prefix, varname, default)

    def int(self, varname: str, default: int=None) -> int:
        return _int(self.app_prefix, varname, default)