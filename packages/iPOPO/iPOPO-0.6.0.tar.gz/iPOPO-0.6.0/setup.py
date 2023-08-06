#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
iPOPO installation script

:author: Thomas Calmant
:copyright: Copyright 2015, isandlaTech
:license: Apache License 2.0
:version: 0.6.0
:status: Beta

..

    Copyright 2015 isandlaTech

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

# Module version
__version_info__ = (0, 6, 0)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

# ------------------------------------------------------------------------------

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# ------------------------------------------------------------------------------


def read(fname):
    """
    Utility method to read the content of a whole file
    """
    with open(os.path.join(os.path.dirname(__file__), fname)) as fd:
        return fd.read()

setup(
    name='iPOPO',
    version=__version__,
    license='Apache License 2.0',
    description='A service-oriented component model framework',
    long_description=read('README.rst'),
    author='Thomas Calmant',
    author_email='thomas.calmant@gmail.com',
    url='https://ipopo.coderxpress.net/',
    packages=[
        'pelix',
        'pelix.http',
        'pelix.internals',
        'pelix.ipopo',
        'pelix.ipopo.handlers',
        'pelix.misc',
        'pelix.remote',
        'pelix.remote.discovery',
        'pelix.remote.transport',
        'pelix.services',
        'pelix.shell'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ],
    install_requires=['jsonrpclib-pelix'],
    extras_require={
        'MQTT': ['paho-mqtt'],
        'XMPP': ['sleekxmpp'],
        'zeroconf': ['pyzeroconf']
    }
)
