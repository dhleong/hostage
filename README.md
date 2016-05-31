hostage [![PyPI](http://img.shields.io/pypi/v/hostage.svg?style=flat)](https://pypi.python.org/pypi/hostage) [![Build Status](http://img.shields.io/travis/dhleong/hostage.svg?style=flat)](https://travis-ci.org/dhleong/hostage)
=======

*You'll WANT to release it*

## What

Hostage is a python library for writing awesome release scripts. Build tools
like Gradle are great for building things, but might be cumbersome for taking
those things you've built and sharing them with the world. 

Hostage is simple. Hostage *wants* to be released.

## How

    pip install hostage


Here's a sample release script for Android, with some inline documentation:

```python
#!/usr/bin/env python

import sys
from hostage import *

# prepare some shared vars:
releaseType = sys.argv[1]
slack = slack.Notifier("https://hooks.slack.com/your/hook")
gradlew = gradle.Gradle()

# verify some preconditions. these will always execute:
verify(releaseType in ['Beta', 'Play']) \
    .orElse(echoAndDie("Invalid release type `%s`" % releaseType))
verify(gradlew.hasLocalWrapper()).orElse(echoAndDie("Run from project root"))
verify(Grep("stopship").foundAny(silent=False)).then(echoAndDie("I don't think so"))

# extract the version from the build script. This will look for something like:
#   def VERSION_NAME = '1.0.0'
version = verify(File("app/build.gradle") \
            .filtersTo(gradle.Def("VERSION_NAME")) \
            ).valueElse(echoAndDie("No VERSION_NAME"))

# you can also use regular python, if you prefer:
if git.Tag(version).exists():
    print("Tag for version %s already exists" % version)
    print("Update VERSION_NAME first")
    exit(1)

# read some release notes; this snippet will reuse an existing
#  notes file if it exists (in case you bailed below) so you
#  don't have to rewrite your notes from scratch
notes = File("notes")
contents = verify(notes.contents()).valueElse(buildDefaultNotes)
notes.delete()

# Edit() attempts to open an editor for creating (or editing)
#  a file, optionally with some initial content. Currently,
#  we support doing this with Vim
verify(Edit(notes, withContent=contents).didCreate())\
        .orElse(echoAndDie("Aborted due to empty message"))

count = len(notes.contents())
verify(count <= 500).orElse(echoAndDie("Character limit is 500! You have %d" % count))

# run your tests and build your apk
assemble = 'assemble' + releaseType + 'Release'
test = 'test' + releaseType + 'Release'

# Note the new syntax here: by wrapping the Evaluator (gradlew) in
#  verify(), instead of the method call result, you get "dry run"
#  capability for free. Passing --dryrun to your script will cause
#  all such calls to succeed, and print the arguments for verification.
verify(gradlew).executes("clean " + assemble + " " + test).orElse(die())

# Dry run is particularly useful for verifying you've passed correct
#  arguments to something like the Google Play Store APK updater:
verify(playstore.Update(
    package='your.awesome.app',
    apk='build/outputs/apk/app-%s-release.apk' % releaseType.lower(),
    whatsnew={ 'en-US': notes.contents() },
    track='beta')
    ).publish().orElse(die())

# Dryrun also lets you avoid doing things until you're ready to run
#  for real, like creating git tags...
versionTag = git.Tag(version)
verify(versionTag).create()
verify(versionTag).push('origin') 

# ... or notifying your Slack room
verify(slack).notify("Released %s %s!" % (releaseType, version))

# now, just clean up and done!
notes.delete()
print("Done!")
```
