#!/usr/bin/env python

import codecs
import os
import sys
from distutils.core import setup

from setuptools import find_packages


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload -r pypi')
    sys.exit()

PACKAGE_VERSION = '0.0.9'
PACKAGE_DOWNLOAD_URL = (

)


def read_file(filename):
    """Read a utf8 encoded text file and return its contents."""
    with codecs.open(filename, 'r', 'utf8') as f:
        return f.read()


setup(
    name='python-dateconv',
    version=PACKAGE_VERSION,
    license=read_file('LICENSE.txt'),
    packages=find_packages(),
    long_description=read_file('README.rst'),
    author='Sapronov Alexander',
    url='https://github.com/WarmongeR1/python-dateconv',
    author_email='sapronov.alexander92@gmail.com',
    description='Package for date convert between formats ',
    include_package_data=True,
    keywords=[
        'converter', 'time', 'datetime', 'unix time'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.3',
        'Programming Language :: Python :: 3.4',
        'Natural Language :: English',
    ],
)
