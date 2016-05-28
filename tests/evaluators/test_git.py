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

class TestLog:
    def test_output(self):
        log = git.Log(path="946b5ac..3dd3811", pretty="format:- %s")
        res = log.output()
        assert res == "- Convert git stuff to new Evaluator"
