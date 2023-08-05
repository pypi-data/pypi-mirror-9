#!/usr/bin/env python

from distutils.core import setup

VERSION = '0.1.1'

setup(name='django-mediagenie',
      version=VERSION,
      author='Martin Camacho',
      author_email='martin@kensho.com',
      license='MIT',
      description='Static files management for Django',
      url = 'https://github.com/mcamac/django-media-genie',
      download_url = 'https://github.com/mcamac/django-media-genie/tarball/%s' % VERSION,
      packages=['mediagenie'])
