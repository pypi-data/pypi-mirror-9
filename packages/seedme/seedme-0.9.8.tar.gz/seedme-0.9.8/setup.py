#!/usr/bin/env python
"""Setup script for SeedMe python client"""

import os
import sys

# Bail if python < 2.6
if sys.version_info > (2, 6,):
    print ("Python version is compatible with this module")
else:
    print ("ERROR: Python 2.6.x + is required for this module")
    sys.exit(1)


try:
    from setuptools import setup
    print ("\n**** Using setuptools ****\n")
except ImportError:
    try: # if all dependencies are installed we can just use distutils
        import argparse, collections, json, requests
        from distutils.core import setup
        print ("\n**** Using distutils ****\n")
    except ImportError: # use ez_setup which will download and install dependencies
        # use shipped ez_setup
        import thirdparty.ez_setup
        thirdparty.ez_setup.use_setuptools()
        from setuptools import setup
        print ("\n**** Using ez_setup ****\n")


# collect missing dependencies
deps = []


try:
    import argparse
except ImportError:
    # use backport for python 2.6
    deps.append('argparse')

try:
    from collections import OrderedDict
except ImportError:
    # use backport for python 2.6
    deps.append('OrderedDict')

try:
    import json
except ImportError:
    # use backport for python 2.6
    deps.append('simplejson')

try:
    import requests
except ImportError:
    deps.append('requests')

# get license txt if available
license = ''
if os.path.isfile('LICENSE.txt'):
    with open('LICENSE.txt') as file:
        license = file.read()

# add long_description from file if available
long_description = ''
if os.path.isfile('README.rst'):
    with open('README.rst') as file:
        long_description = file.read()
else:
    long_description='seedme.py: Uploads, downloads and queries content at ' +\
                   'SeedMe.org. This module provides command line '    +\
                   'interface as well as methods and api for '         +\
                   'programmatic usage. It performs extensive sanity ' +\
                   'checks input data and is kept upto date with '     +\
                   'REST api at SeedMe.org.',

setup(name='seedme',
      version="0.9.8",
      author='Amit Chourasia',
      description='Python REST client for SeedMe.org',
      long_description=long_description,
      license=license,
      url="https://www.seedme.org/downloads",
      download_url='https://bitbucket.org/seedme/seedme-python-client/overview',
      install_requires=deps,
      entry_points={"console_scripts": ["seedme = seedme:main"]},
      py_modules=['seedme'],
      scripts=['seedme.py'],
     )
