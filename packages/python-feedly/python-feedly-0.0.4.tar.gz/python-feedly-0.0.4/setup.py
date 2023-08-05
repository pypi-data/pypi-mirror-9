#!/usr/bin/env python

import codecs
import os
from setuptools import find_packages
import sys
from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload -r pypi')
    sys.exit()

PACKAGE_VERSION = '0.0.4'
PACKAGE_DOWNLOAD_URL = (

)


def read_file(filename):
    """
    Read a utf8 encoded text file and return its contents.
    """
    with codecs.open(filename, 'r', 'utf8') as f:
        return f.read()

setup(
    name='python-feedly',
    version=PACKAGE_VERSION,
    license=read_file('LICENSE.txt'),
    packages=find_packages(),
    long_description=read_file('README.rst'),
    author='Alexander Sapronov',
    author_email='sapronov.alexander92@gmail.com',
    description='Client for Feedly.com',
    url='https://github.com/WarmongeR1/python-feedly',
    include_package_data=True,
    install_requires=[
        'requests',
    ],
)
