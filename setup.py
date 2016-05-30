#!/usr/bin/env python

import re

from setuptools import setup

packages = ['hostage']

requires = [
    'requests>=2.10.0', 
    'PyGithub>=1.26.0', 
    'google-api-python-client>=1.3.2'
]

test_requirements = ['pytest>=2.8.0', 'responses>=0.5.1', 'mock']


with open('hostage/__init__.py', 'r') as fp:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fp.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
  name='hostage',
  version=version,
  description="You'll WANT to release it",
  author='Daniel Leong',
  author_email='me@dhleong.net',
  url='https://github.com/dhleong/hostage', # use the URL to the github repo
  packages=packages, 
  package_dir={'hostage': 'hostage'},
  install_requires=requires,
  tests_require=test_requirements,
  download_url='https://github.com/dhleong/hostage/tarball/' + version, 
  keywords=['release', 'script'], 
  classifiers=[],
)
