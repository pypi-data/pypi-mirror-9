#!/usr/bin/env python

import os
from setuptools import setup, find_packages

sdict = dict(
  name = 'django-moj-template',
  packages = find_packages(),
  version = '0.23.1',
  description = 'MOJ Template',
  long_description = 'A base template for Ministry of Justice Services based on the GOV.UK template.',
  url = 'https://github.com/ministryofjustice/moj_template',
  author = 'MOJ Digital Services',
  author_email = 'dom.smith@digital.justice.gov.uk',
  maintainer = 'Dom Smith',
  maintainer_email = 'dom.smith@digital.justice.gov.uk',
  keywords = ['python', 'django', 'ministryofjustice', 'govuk'],
  license = 'MIT',
  include_package_data = True,
  install_requires = [
    'django>=1.3'
  ],
  platforms=["any"],
  classifiers=[
    'Programming Language :: Python',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ]
)

from distutils.core import setup
setup(**sdict)
