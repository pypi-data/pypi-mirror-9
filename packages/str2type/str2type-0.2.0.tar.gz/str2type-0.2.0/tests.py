"""
Unittests for str2type
"""


import codecs
import json
import os


TYPE_LOOP = (
    ('1', int),
    ('1.', float),
    ('.1', float),
    ('nONe', lambda x: None),
    ('fALse', lambda x: False),
    ('tRUe', lambda x: True),
    ('string', str),
    ('{"K3": [0, 1, 2, 3, 4], "UPPERCASE": "v2", "k1": "MORE UPPERCASE"}', json.loads),
    (codecs.encode(os.linesep, 'unicode_escape'), lambda x: codecs.decode(x, 'unicode_escape'))
)

from str2type import click_callback
from str2type import str2type


def test_true():
    assert str2type("TrUe") is True


def test_false():
    assert str2type("FaLsE") is False


def test_none():
    assert str2type("NoNe") is None


def test_int():
    assert str2type("123") is 123


def test_float():
    assert str2type("1.23") == 1.23


def test_str():
    assert str2type("Some string") == "Some string"


def test_json():
    s = '{"K3": [0, 1, 2, 3, 4], "UPPERCASE": "v2", "k1": "MORE UPPERCASE"}'
    assert str2type(s) == json.loads(s)


def test_malformed_json():
    s = '{"k3": [0, 1, 2, 3, 4], "k2": "v2", "k1": "v1"}'
    assert str2type(s[1:]) == s[1:]


def test_float_no_mantissa():
    # Mantissa = numbers to the right of the decimal
    s = '1.'
    assert str2type(s) == float(s)


def test_float_no_integer_part():
    s = '.1'
    assert str2type(s) == float(s)


def test_invalid_type():
    try:
        str2type(None)
        assert True is False, "ERROR: Above test should have raised a TypeError"
    except TypeError:
        pass


def test_json_nul():
    s = 'nul'
    assert str2type(s) == s


def test_decode_escape():
    s = codecs.encode(os.linesep, 'unicode_escape')
    assert str2type(s) == os.linesep


def test_no_decode_escape():
    s = str(codecs.encode(os.linesep, 'unicode_escape'))
    assert str2type(s, decode_escape=False) == s


def test_click_callback():
    for val, cast in TYPE_LOOP:
        assert click_callback(None, None, val) == cast(val)
