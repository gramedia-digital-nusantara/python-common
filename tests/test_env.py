from collections import defaultdict
from unittest.mock import patch, MagicMock

from gramedia.common.env import _str, _int, _bool, EnvConfig


def fake_getenv(param_name: str) -> str:
    """ Mock the functionality of `os.getenv`
    """
    fake_env = defaultdict(
        lambda: None,
        GM_SOME_STRING='http://some-string',
        GM_SOME_INT='1',
        GM_SOME_BOOL_t='t',
        GM_SOME_BOOL_T='T',
        GM_SOME_BOOL_1='1',
        GM_SOME_BOOL_f='0',
        GM_PG_URI='postgresql://dj:p@ssw0rd24@some_server:5432/gramedia',
        GM_SQLITE_URI='sqlite3:///some-path/on/disk/db.sqlite3'
    )
    return fake_env[param_name]


@patch('gramedia.common.env.getenv', new=fake_getenv)
def test_string_envvar():
    """ String env vars parse properly.
    """
    assert _str('GM', 'SOME_STRING') == "http://some-string"

    assert _str('GM', 'MISSING_VAR') is None


@patch('gramedia.common.env.getenv', new=fake_getenv)
def test_int_envvar():
    """ Integer env vars parse properly
    """
    assert _int('GM', 'SOME_INT') == 1
    assert _int('GM', 'MISSING_VAR') is None


@patch('gramedia.common.env.getenv', new=fake_getenv)
def test_bool_envvar():
    assert _bool('GM', 'SOME_BOOL_t') is True
    assert _bool('GM', 'SOME_BOOL_T') is True
    assert _bool('GM', 'SOME_BOOL_1') is True

    assert _bool('GM', 'SOME_BOOL_f') is False

    assert _bool('GM', 'MISSING_VAR') is None

    assert _bool('GM', 'MISSING_VAR', False) is False


@patch('gramedia.common.env.getenv', new=fake_getenv)
def test_class_based_envconfig():
    """ Ensure that EnvConfig properly parses env vars out to their proper types
    """
    Env = EnvConfig('GM')

    str_mock = MagicMock(wraps=_str)
    with patch('gramedia.common.env._str', new=str_mock) as mock:
        assert Env.string('SOME_STRING') == "http://some-string"
        mock.assert_called_once_with('GM', 'SOME_STRING', None)

    bool_mock = MagicMock(wraps=_bool)
    with patch('gramedia.common.env._bool', new=bool_mock) as mock:
        assert Env.boolean('SOME_BOOL_t') is True
        mock.assert_called_once_with('GM', 'SOME_BOOL_t', None)

    int_mock = MagicMock(wraps=_int)
    with patch('gramedia.common.env._int', new=int_mock) as mock:
        assert Env.int('SOME_INT') == 1
        mock.assert_called_once_with('GM', 'SOME_INT', None)


@patch('gramedia.common.env.getenv', new=fake_getenv)
def test_django_db_uri_pg_mysql_oracle():
    """ Ensure that database URIs can be used.
    """
    Env = EnvConfig('GM')

    expected = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gramedia',
        'USER': 'dj',
        'PASSWORD': 'p@ssw0rd24',
        'HOST': 'some_server',
        'PORT': '5432',
    }

    assert Env.django_db('PG_URI') == expected


@patch('gramedia.common.env.getenv', new=fake_getenv)
def test_django_db_uri_sqlite():
    """ Ensure SQLite database URIs parse
    """
    Env = EnvConfig('GM')

    expected = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/some-path/on/disk/db.sqlite3'
    }

    assert Env.django_db('SQLITE_URI') == expected
