"""
Unittests for str2type
"""


import codecs
import json
import os

import str2type


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


def test_true():
    assert str2type.str2type("TrUe") is True


def test_false():
    assert str2type.str2type("FaLsE") is False


def test_none():
    assert str2type.str2type("NoNe") is None


def test_int():
    assert str2type.str2type("123") is 123


def test_float():
    assert str2type.str2type("1.23") == 1.23


def test_str():
    assert str2type.str2type("Some string") == "Some string"


def test_json():
    s = '{"K3": [0, 1, 2, 3, 4], "UPPERCASE": "v2", "k1": "MORE UPPERCASE"}'
    assert str2type.str2type(s) == json.loads(s)


def test_malformed_json():
    s = '{"k3": [0, 1, 2, 3, 4], "k2": "v2", "k1": "v1"}'
    assert str2type.str2type(s[1:]) == s[1:]


def test_float_no_mantissa():
    # Mantissa = numbers to the right of the decimal
    s = '1.'
    assert str2type.str2type(s) == float(s)


def test_float_no_integer_part():
    s = '.1'
    assert str2type.str2type(s) == float(s)


def test_invalid_type():
    try:
        str2type.str2type(None)
        assert True is False, "ERROR: Above test should have raised a TypeError"
    except TypeError:
        pass


def test_json_nul():
    s = 'nul'
    assert str2type.str2type(s) == s


def test_decode_escape():
    s = codecs.encode(os.linesep, 'unicode_escape')
    assert str2type.str2type(s) == os.linesep


def test_no_decode_escape():
    s = str(codecs.encode(os.linesep, 'unicode_escape'))
    assert str2type.str2type(s, decode_escape=False) == s


def test_click_callback():
    for val, cast in TYPE_LOOP:
        assert str2type.click_callback(None, None, val) == cast(val)


def test_click_callback_key_val_to_dict():
    content = ['key1=NOnE', 'key2=1', 'key4=1.']
    expected = {param.split('=')[0]: str2type.str2type(param.split('=')[1]) for param in content}
    result = str2type.click_callback_key_val_dict(None, None, content)
    assert isinstance(result, dict)
    assert len(result) is len(content)
    for key, val in result.items():
        assert val == expected[key], "Expected: `%s' - Actual: `%s'" % (expected[key], val)


def test_click_callback_key_val_to_dict_bad_format():
    try:
        str2type.click_callback_key_val_dict(None, None, ('good=formatting', 'bad_formatting'))
        assert True is False, "ERROR: The above test should have thrown a ValueError"
    except ValueError:
        pass