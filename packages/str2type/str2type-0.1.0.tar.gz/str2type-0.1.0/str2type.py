"""
Convert a Python string to its native type
"""


import json


__version__ = "0.1.0"
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


# Allow the user to specify which JSON library to use for decoding.  Must support `json.loads`
# and some additional requirements, which can be found in str2type.__doc__
JSON = json


def str2type(string, json_lib=JSON):

    """
    Convert a string representation of an int, float, None, True, False, or JSON
    to its native type.  For None, True, and False, case is irrelevant.

        >>> from str2type import str2type
        >>> print(str2type("1.23"))
        1.23

    The user can also specify which JSON library to use for decoding should
    they know they will be encountering a lot of JSON, in which case a different
    library is probably more appropriate than this function.

        >>> from str2type import str2type
        >>> import ujson
        >>> print(str2type('[0,1,2,3,4]', json_lib=ujson))
        [0, 1, 2, 3, 4]

    Alternatively:

        >>> import str2type
        >>> import ujson
        >>> str2type.JSON = ujson
        >>> print(str2type('FaLsE'))
        False

    The brunt of the decoding is handled by `json`, which can decode all supported
    types except for strings and `None`.  If the user specifies a different JSON
    library it is still expected to be able to handle these types.

    Parameters
    ----------
    string : str
        Input string to transform

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

    string_strip = string.strip()

    # Json is immediately recognized
    try:
        return json_lib.loads(string_strip)

    except ValueError:

        # Handle situations like TrUe or False
        try:
            return json.loads(string_strip.lower())

        except ValueError:

            # None must be manually checked because it appears as 'nul' in JSON
            if string_strip.lower() == 'none':
                return None

            # Couldn't decode anything - return the input string
            else:
                return string
