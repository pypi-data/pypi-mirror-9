# -*- coding: utf-8 -*-
from distutils.core import setup


setup(
  name = 'python-artsy',
  packages = ['artsy'],
  version = '1.1',
  description = 'Python client for Artsy.',
  author = 'Rodrigo Savian',
  author_email = 'rodrigosavian@gmail.com',
  url = 'https://github.com/rodrigosavian/python-artsy',
  download_url = 'https://github.com/rodrigosavian/python-artsy/tarball/1.1',
  keywords = ['artsy', 'python', 'client', 'api'],
  install_requires=[
    'requests==2.6.0',
  ],
  classifiers = [],
)
