#!/usr/bin/env python

import os
import sys

from setuptools import setup, find_packages

# remove MANIFEST. distutils doesn't properly update it when the contents of directories change.
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

# Grab description for Pypi
with open('README') as fhl:
    description = fhl.read()

setup(
        name             = 'django-fast-fixtures',
        version          = '0.7',
        description      = 'Replace dumpdata and loaddata with migration aware fixture commands.',
        long_description = description,
        url              = 'https://github.com/doctormo/django-fast-fixtures',
        author           = 'Martin Owens',
        author_email     = 'doctormo@gmail.com',
        platforms        = 'linux',
        license          = 'LGPLv3',
        packages         = find_packages(),
        install_requires = [
          'django>=1.7.4',
        ],
    )

