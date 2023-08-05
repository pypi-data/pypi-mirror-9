#!/usr/bin/env python


"""
Setup script for str2type
"""


import setuptools

import str2type


with open('README.md') as f:
    readme = f.read().strip()


setuptools.setup(
    name='str2type',
    version=str2type.__version__,
    author=str2type.__author__,
    author_email=str2type.__email__,
    description="Convert a string representation of an int, float, None, True, False, or JSON to its native type.  \
    For None, True, and False, case is irrelevant.",
    long_description=readme,
    url=str2type.__source__,
    license=str2type.__license__,
    py_modules=['str2type'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    include_package_data=True,
    zip_safe=True,
    keywords='python string to type string2type str2type'
)
