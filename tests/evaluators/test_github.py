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

class FakeRepo:
    def __init__(self):
        self.milestones = {}

    def get_milestone(self, number):
        return self.milestones.get(number)

    def get_milestones(self):
        return self.milestones.values()

class GhObj:
    def __init__(self, data):
        self.data = data

    def __getattr__(self, attr):
        if attr in self.data:
            return self.data[attr]

        raise AttributeError

@pytest.fixture
def conf():
    conf = github.Config(repo="serenity/engineering", 
            token="kayleesawesometoken")
    conf._repo = FakeRepo()
    return conf

@pytest.fixture
def repo(conf):
    return conf._repo

class TestMilestone:
    def test_exists_fail(self, conf):
        m = github.Milestone("keep-flyin", config=conf)
        assert m.exists() == False

    def test_exists_pass(self, conf, repo):
        repo.milestones[1] = GhObj({
            "number": 1,
            "title":"keep-flyin"
            })
        m = github.Milestone("keep-flyin", config=conf)
        assert m.exists() == True

    def test_edit(self, conf, repo):
        edits = []
        def doEdit(**kwargs):
            edits.append(kwargs)

        repo.milestones[1] = GhObj({
            "number": 1,
            "title":"keep-flyin"
            })
        repo.milestones[1].edit = doEdit

        m = github.Milestone("keep-flyin", config=conf)
        m.edit(state="closed", \
                description="Replace compression coil")

        edit = edits[-1]
        # NB: title is a required arg, so we fill it in
        #  if it wasn't provided
        assert edit['title'] == 'keep-flyin'

        m.edit(title="emergency")
        edit = edits[-1]
        # ... but don't override if it was
        assert edit['title'] == 'emergency'

