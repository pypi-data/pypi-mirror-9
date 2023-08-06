#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import python libs
import os
import sys

if 'USE_SETUPTOOLS' in os.environ or 'setuptools' in sys.modules:
    from setuptools import setup
else:
    from distutils.core import setup

NAME = 'libnacl'
DESC = ('Python bindings for libsodium/tweetnacl based on ctypes')

# Version info -- read without importing
_locals = {}
with open('libnacl/version.py') as fp:
    exec(fp.read(), None, _locals)
VERSION = _locals['__version__']

setup(name=NAME,
      version=VERSION,
      description=DESC,
      author='Thomas S Hatch',
      author_email='thatch@saltstack.com',
      url='https://libnacl.readthedocs.org/',
      classifiers=[
          'Operating System :: OS Independent',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Topic :: Security :: Cryptography',
          ],
      packages=['libnacl'])
