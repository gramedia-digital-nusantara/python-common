from collections import defaultdict
from unittest.mock import patch, MagicMock

from gramedia.common.env import _str, _int, _bool, EnvConfig


def fake_getenv(param_name: str) -> str:
    """ Mock the functionality of `os.getenv`
    """
    d = defaultdict(
        lambda: None,
        GM_SOME_STRING="http://some-string",
        GM_SOME_INT="1",
        GM_SOME_BOOL_t="t",
        GM_SOME_BOOL_T="T",
        GM_SOME_BOOL_1="1",
        GM_SOME_BOOL_f="0"
    )
    return d[param_name]


@patch('gramedia.common.env.getenv', new=fake_getenv)
def test_string_envvar():
    assert _str("GM", "SOME_STRING") == "http://some-string"

    assert _str("GM", "MISSING_VAR") is None


@patch('gramedia.common.env.getenv', new=fake_getenv)
def test_int_envvar():
    assert _int("GM", "SOME_INT") == 1
    assert _int("GM", "MISSING_VAR") is None


@patch('gramedia.common.env.getenv', new=fake_getenv)
def test_bool_envvar():
    assert _bool("GM", "SOME_BOOL_t") == True
    assert _bool("GM", "SOME_BOOL_T") == True
    assert _bool("GM", "SOME_BOOL_1") == True

    assert _bool("GM", "SOME_BOOL_f") == False

    assert _bool("GM", "MISSING_VAR") is None

    assert _bool("GM", "MISSING_VAR", False) == False


@patch('gramedia.common.env.getenv', new=fake_getenv)
def test_class_based_envconfig():
    E = EnvConfig("GM")

    str_mock = MagicMock(wraps=_str)
    with patch('gramedia.common.env._str', new=str_mock) as mock:
        assert "http://some-string" == E.string("SOME_STRING")
        mock.assert_called_once_with("GM", "SOME_STRING", None)

    bool_mock = MagicMock(wraps=_bool)
    with patch('gramedia.common.env._bool', new=bool_mock) as mock:
        assert True == E.boolean("SOME_BOOL_t")
        mock.assert_called_once_with("GM", "SOME_BOOL_t", None)

    int_mock = MagicMock(wraps=_int)
    with patch('gramedia.common.env._int', new=int_mock) as mock:
        assert 1 == E.int("SOME_INT")
        mock.assert_called_once_with("GM", "SOME_INT", None)
