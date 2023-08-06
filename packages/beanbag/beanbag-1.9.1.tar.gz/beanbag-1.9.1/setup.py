#!/usr/bin/env python

from setuptools import setup, find_packages

import codecs, os.path, re

here = os.path.abspath(os.path.dirname(__file__))

# Read the version number from a source file.
# Why read it, and not import?
# see https://groups.google.com/d/topic/pypa-dev/0PkjVpcxTzQ/discussion
def find_version(*file_paths):
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    with codecs.open(os.path.join(here, *file_paths), 'r', 'latin1') as f:
        version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

with codecs.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'beanbag',
  version = find_version('beanbag', '__init__.py'),
  description = 'A helper module for accessing REST APIs',
  long_description = long_description,
  packages=find_packages(exclude=["contrib", "docs", "tests*"]),

  install_requires = ['requests >= 0.12.1'],

  url = 'https://github.com/ajtowns/beanbag',

  author = 'Anthony Towns',
  author_email = 'aj@erisian.com.au',

  license = 'MIT',

  classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
  ],
)
