str2type
========

[![Build Status](https://travis-ci.org/geowurster/str2type.svg?branch=master)](https://travis-ci.org/geowurster/str2type)

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


Installing
----------

Via pip:

    $ pip install str2type

From master branch
    
    $ git clone https://github.com/geowurster/str2type
    $ pip install ./str2type/


Developing
----------

Install:

    $ pip install virtualenv
    $ git clone https://github.com/geowurster/str2type
    $ cd str2type
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements-dev.txt
    $ pip install -e .

Test:
    
    $ nosetests \
        --with-coverage \
        --cover-package=str2type \
        --cover-erase \
        --cover-inclusive

Lint:

    $ pep8 --max-line-length=120 str2type
