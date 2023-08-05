"""
Unittests for str2type
"""


import json


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


def test_json_null():
    # JSON maps null to None but null is a valid string value.  Make sure it passes through
    s = 'null'
    assert str2type(s) == s
