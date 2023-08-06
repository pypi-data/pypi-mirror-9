#!/usr/bin/env python

import os
import sys
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'rwslib',
    'rwslib.rws_requests',
]

rwsinit = open('rwslib/__init__.py').read()
author = re.search("__author__ = '([^']+)'", rwsinit).group(1)
version = re.search("__version__ = '([^']+)'", rwsinit).group(1)

setup(
    name='rwslib',
    version=version,
    description='Rave web services for Python',
    long_description=open('README.md').read(),
    author=author,
    author_email="isparks@mdsol.com",
    packages=packages,
    package_dir={'rwslib': 'rwslib'},
    include_package_data=True,
    install_requires=['requests','lxml','httpretty'],
    license=open('LICENSE.txt').read(),
    zip_safe=False,
    test_suite='rwslib.tests.all_tests',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
