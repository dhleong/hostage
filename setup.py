#!/usr/bin/env python

import os
import sys
import re

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = find_packages(exclude=["tests", "tests.*"])

requires = [
    'python-dateutil>=2.6.0',
    'requests>=2.10.0',
    'PyGithub>=1.26.0',
    'google-api-python-client>=1.3.2'
]

test_requirements = ['pytest>=2.6.0', 'responses>=0.5.1', 'mock']


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
    url='https://github.com/dhleong/hostage',  # use the URL to the github repo
    packages=packages,
    package_dir={'hostage': 'hostage'},
    install_requires=requires,
    tests_require=test_requirements,
    download_url='https://github.com/dhleong/hostage/tarball/' + version,
    keywords=['release', 'script'],
    classifiers=[],
    cmdclass={'test': PyTest}
)
