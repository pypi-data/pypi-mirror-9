"""
Convert a Python string to its native type
"""


import codecs
import json
import sys


__all__ = ['str2type', 'click_callback', 'click_callback_key_val_dict']


__version__ = "0.3.0"
__author__ = "Kevin Wurster"
__email__ = "wursterk@gmail.com"
__source__ = "https://github.com/geowurster/str2type"
__license__ = """
New BSD License

Copyright (c) 2014, Kevin D. Wurster
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* The names of its contributors may not be used to endorse or promote products
  derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


if sys.version_info[0] is 3:  # pragma no cover
    STR_TYPES = (str)
else:  # pragma no cover
    STR_TYPES = (str, unicode)


def str2type(string, decode_escape=True):

    """
    Convert a string representation of an int, float, None, True, False, or JSON
    to its native type.  For None, True, and False, case is irrelevant.  The
    primary use-case of this function is automatically parsing user-input from
    the commandline into Python types.  Argument parsers usually handle this no
    problem but if a flag can take multiple types then `str2type()` can serve
    as the decoder.

        >>> from str2type import str2type
        >>> print(str2type("1.23"))
        1.23
        >>> print(str2type("1.")
        1.0
        >>> print(str2type(".2"))
        0.2
        >>> print(str2type("NonE"))
        None
        >>> print(str2type("String"))
        "String"

    Parameters
    ----------
    string : str
        Input string to transform.
    decode_escape : bool, optional
        Use `codecs.decode(string, 'unicode_escape')` to handle escaped strings
        like \n being passed in from the commandline.  Escape characters end up
        doubly escaped, which is especially annoying for newline characters.

    Returns
    -------
    str
        The input string if it could not be converted to another type or is
        actually just a string.
    list
        If input is JSON.
    dict
        If input is JSON.
    int
        "123" -> 123
    float
        "1.23" -> 1.23
    True
        "TrUe" -> True
    False
        "FaLsE" -> False
    None
        "NoNe" -> None
    """

    if not (isinstance(string, STR_TYPES) or isinstance(string, bytes)):
        raise TypeError("Input string is a '%s' - must be a str or unicode instance" % type(string))

    if decode_escape:
        string = codecs.decode(string, 'unicode_escape')

    processing_string = string.strip()

    # Integers are really easy to grab and must happen before floats otherwise '1' becomes '1.0'
    if processing_string.isdigit():
        return int(processing_string)
    else:

        # Casting to float can just be blindly tried
        try:
            return float(processing_string)
        except ValueError:

            # True, False, and None are evaluated individually to check for mixed case (TrUe, FALse, etc.)
            string_lower = processing_string.lower()
            if string_lower == 'none':
                return None
            elif string_lower == 'true':
                return True
            elif string_lower == 'false':
                return False
            else:

                # Try to decode a JSON object if everything else failed
                try:
                    return json.loads(processing_string)

                # Input must actually just be a string - return the input object
                except ValueError:
                    return string


def click_callback(ctx, param, value):

    """
    Easily integrate `str2type()` into the CLI framework click as a callback
    function to automatically cast commandline arguments to their native Python
    type.  Click already handles this but sometimes values can be of multiple,
    especially for `key=val` arguments that will be passed to a class as
    `**kwargs`.

    Parameters
    ----------
    ctx : click.Context
        Ignored
    param : click.Option
        Ignored
    value : tuple
        All collected key=val values for an option.
    Returns
    -------
    dict
    """

    return str2type(value)


def click_callback_key_val_dict(ctx, param, value):

    """
    Some options like `-ro` take `key=val` pairs that need to be transformed
    into `{'key': 'val}`.  This function can be used as a callback to handle
    all options for a specific flag, for example if the user specifies 3 reader
    options like `-ro key1=val1 -ro key2=val2 -ro key3=val3` then `click` uses
    this function to produce `{'key1': 'val1', 'key2': 'val2', 'key3': 'val3'}`.
    Parameters
    ----------
    ctx : click.Context
        Ignored
    param : click.Option
        Ignored
    value : tuple
        All collected key=val values for an option.
    Returns
    -------
    dict
    """

    output = {}
    for pair in value:
        if '=' not in pair:
            raise ValueError("Incorrect syntax for KEY=VAL argument: `%s'" % pair)
        else:
            key, val = pair.split('=')
            val = str2type(val)
            output[key] = val

    return output
