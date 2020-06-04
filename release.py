#!/usr/bin/env python3
#
# Release script for hostage (using hostage)
#

from hostage import *

version = verify(File('hostage/__init__.py')\
        .filtersTo(RegexFilter("__version__ = '(.*)'"))\
        ).valueElse(echoAndDie("No __version__"))

tag = git.Tag(version)
verify(tag.exists()).then(echoAndDie("Version %s already exists" % version))

verify(Execute('python3 setup.py test')).succeeds(silent=False)
verify(Execute('python3 setup.py publish')).succeeds(silent=False)

verify(tag).create()
verify(tag).push('origin')
