#!/usr/bin/env python

# To upload a version to PyPI, run:
#    python setup.py sdist upload
# If the package is not registered with PyPI yet, do so with:
#     python setup.py register

from distutils.core import setup
import os

__version__ = '1.3.2'

DESCRIPTION = \
    """A wrapper around profile/cProfile, gprof2dot and dot,
providing a simple context manager for profiling sections
of Python code and producing visual graphs of profiling results."""

# Auto generate a __version__ package for the package to import
with open(os.path.join('bprofile', '__version__.py'), 'w') as f:
    f.write("__version__ = '%s'\n" % __version__)

# Ensure graphviz is installed:
from bprofile.bprofile import DOT_PATH

setup(name='bprofile',
      version=__version__,
      description=DESCRIPTION,
      author='Chris Billington',
      author_email='chrisjbillington@gmail.com',
      url='https://bitbucket.org/cbillington/bprofile',
      license="simplified BSD",
      packages=['bprofile'],
      )
