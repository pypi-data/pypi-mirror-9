str2type
========

[![Build Status](https://travis-ci.org/geowurster/str2type.svg?branch=master)](https://travis-ci.org/geowurster/str2type) [![Coverage Status](https://coveralls.io/repos/geowurster/str2type/badge.svg?branch=master)](https://coveralls.io/r/geowurster/str2type)

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


Installing
----------

Via pip:

    $ pip install str2type

From master branch:
    
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
    
    $ nosetests


Coverage:

    $ nosetests --with-coverage

Lint:

    $ pep8 --max-line-length=120 str2type.py
