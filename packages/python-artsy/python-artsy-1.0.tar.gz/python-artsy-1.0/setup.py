# -*- coding: utf-8 -*-
from distutils.core import setup


setup(
  name = 'python-artsy',
  packages = ['artsy'], # this must be the same as the name above
  version = '1.0',
  description = 'Python client for Artsy.',
  author = 'Rodrigo Savian',
  author_email = 'rodrigosavian@gmail.com',
  url = 'https://github.com/rodrigosavian/python-artsy',
  download_url = 'https://github.com/rodrigosavian/python-artsy/tarball/1.0',
  keywords = ['artsy', 'python', 'client', 'api'],
  install_requires=[
    'requests==2.6.0',
  ],
  classifiers = [],
)
