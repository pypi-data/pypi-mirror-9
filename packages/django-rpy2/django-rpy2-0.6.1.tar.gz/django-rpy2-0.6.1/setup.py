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
        name             = 'django-rpy2',
        version          = '0.6.1',
        description      = 'Allow django to create R scripts and generate charts and other data output from those scripts.',
        long_description = description,
        url              = 'https://bitbucket.net/charts',
        author           = 'Martin Owens',
        author_email     = 'doctormo@gmail.com',
        platforms        = 'linux',
        license          = 'AGPLv3',
        packages         = find_packages(),
        install_requires = [
          'django>=1.7.4',
          'django-object-actions>=0.5.1',
          'rpy2>=2.5.6',
        ],
    )

