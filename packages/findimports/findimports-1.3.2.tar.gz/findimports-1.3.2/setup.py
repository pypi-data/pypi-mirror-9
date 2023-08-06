#!/usr/bin/env python
import ast
import os
import re
import email.utils
from setuptools import setup


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


metadata = dict(
    (k, ast.literal_eval(v)) for k, v in
    re.findall('^(__version__|__author__|__url__|__licence__) = (.*)$',
               read('findimports.py'), flags=re.MULTILINE)
)
version = metadata['__version__']
author, author_email = email.utils.parseaddr(metadata['__author__'])
url = metadata['__url__']
licence = metadata['__licence__']


setup(
    name='findimports',
    version=version,
    author=author,
    author_email=author_email,
    url=url,
    description='Python module import analysis tool',
    long_description=read('README.rst') + '\n\n' + read('CHANGES.rst'),
    license=licence,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU General Public License (GPL)'
            if licence.startswith('GPL') else
        'License :: OSI Approved :: MIT License'
            if licence.startswith('MIT') else
        'License :: uhh, dunno',
    ],

    py_modules=['findimports'],
    test_suite='testsuite',
    zip_safe=False,
    entry_points="""
    [console_scripts]
    findimports = findimports:main
    """,
)
