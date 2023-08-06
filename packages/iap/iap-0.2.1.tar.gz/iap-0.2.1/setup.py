#!/usr/bin/env python

import os
import sys

from setuptools import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py register sdist upload')
    os.system('python setup.py register bdist_wheel upload')
    sys.exit()


setup(
    name='iap',
    version='0.2.1',
    description='Python utilities for working with Apple In-App Purchases (IAP)',
    author='Educreations Engineering',
    author_email='engineering@educreations.com',
    url='https://github.com/educreations/python-iap',
    py_modules=['iap'],
    install_requires=['pycrypto', 'django', 'requests'],
)
