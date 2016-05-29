#!/usr/bin/env py.test
#
# Github class tests
#

import pytest

import responses

from hostage import github, Execute

@pytest.fixture
def tmpgit(tmpdir, request):
    tmpRoot = tmpdir.mkdir("hostage-test")
    oldRoot = tmpRoot.chdir()
    Execute("git init").succeeds()
    Execute("git remote add origin git@github.com:dhleong/hostage-test.git").succeeds()

    def fin():
        tmpRoot.remove()
        oldRoot.chdir()
    request.addfinalizer(fin)
    return tmpRoot

def test_auto_config(tmpgit):
    tmpgit.join('.github.token').write("mytoken")

    conf = github.Config()
    assert conf.repoName == 'dhleong/hostage-test'
    assert conf.token == 'mytoken'
