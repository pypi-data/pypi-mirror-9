#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '0.1.5'

setup(name='django-mediagenie',
      version=VERSION,
      author='Martin Camacho',
      author_email='martin@kensho.com',
      license='MIT',
      description='Static files management for Django',
      url = 'https://github.com/mcamac/django-media-genie',
      download_url = 'https://github.com/mcamac/django-media-genie/tarball/%s' % VERSION,
      packages=find_packages(exclude=('sample_project', 'sample_project.*', 'dist')))
