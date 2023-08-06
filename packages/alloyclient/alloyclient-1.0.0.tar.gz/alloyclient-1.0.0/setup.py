# -*- coding: utf-8 -*-
"""Setup for Alloy.

Copyright 2014 Archive Analytics Solutions

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
import inspect
import os

from pip.req import parse_requirements
try:
    from pip.download import PipSession
except ImportError:
    # Old pip
    pass

# Import Setuptools
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

# Import our own module here for version number
import alloyclient

# Inspect to find current path
setuppath = inspect.getfile(inspect.currentframe())
setupdir = os.path.dirname(setuppath)

# Find longer description from README
with open(os.path.join(setupdir, 'README.rst'), 'r') as fh:
    _long_description = fh.read()

# Requirements
with open(os.path.join(setupdir, 'requirements.txt'), 'r') as fh:
    try:
        raw_reqs = parse_requirements('requirements.txt', session=PipSession())
    except NameError:
        # Old pip
        raw_reqs = parse_requirements('requirements.txt')

    _install_requires = [
        str(req.req)
        for req
        in raw_reqs
        if req
    ]


setup(
    name='alloyclient',
    version=alloyclient.__version__,
    description='Alloy Client',
    packages=find_packages(),
    install_requires=_install_requires,
    extras_require={
          'docs': ["sphinx"],
    },
    long_description=_long_description,
    author='John Harrison',
    author_email='john.harrison@archiveanalytics.com',
    license="Apache License, Version 2.0",
    url='https://bitbucket.org/archiveanalytics/alloy-client',
    setup_requires=['setuptools-git'],
    entry_points={
        'console_scripts': [
            "alloy = alloyclient.ui:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: System :: Archiving"
    ],
)
