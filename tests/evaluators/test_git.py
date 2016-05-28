#!/usr/bin/env py.test
#
# Git class tests
#

from hostage.evaluators import git

class TestTag:
    def test_exists(self):
        res = git.Tag("nosuch-tag").exists()
        assert res == False

    def test_createAndDelete(self):
        tag = git.Tag("test-tag")
        assert tag.exists() == False

        created = tag.create()
        assert created == True
        assert tag.exists() == True

        deleted = tag.delete()
        assert deleted == True
        assert tag.exists() == False
