#!/usr/bin/env python

from distutils.core import setup
from spanner import __version__

setup(
    name='spanner',
    version=__version__,
    description='An accumulation of utilities / convenience functions for python',
    author='Bryan Johnson',
    author_email='d.bryan.johnson@gmail.com',
    packages=['spanner'],
    url='https://github.com/dbjohnson/python-utils',
    download_url='https://github.com/dbjohnson/spanner/tarball/%s' % __version__
)
