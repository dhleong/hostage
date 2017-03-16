#!/usr/bin/env py.test
#
# Git class tests
#

from hostage.evaluators import git


class TestTag:
    def test_exists(self):
        res = git.Tag("nosuch-tag").exists()
        assert res is False

    def test_createAndDelete(self):
        tag = git.Tag("test-tag")
        assert tag.exists() is False

        created = tag.create()
        assert created is True
        assert tag.exists() is True

        deleted = tag.delete()
        assert deleted is True
        assert tag.exists() is False

    def test_get_created_date(self):
        tag = git.Tag("0.2.0")
        date = tag.get_created_date()
        assert date is not None
        assert date.year == 2017
        assert date.month == 1
        assert date.day == 3


class TestLog:
    def test_output(self):
        log = git.Log(path="946b5ac..3dd3811", pretty="format:- %s")
        res = log.output()
        assert res == "- Convert git stuff to new Evaluator"

    def test_grepList(self):
        log = git.Log(path="946b5ac..cfa1271",
                grep=["test for git.Log", "github milestone"],
                pretty="format:%s")
        res = log.output()
        assert res == "Support editing github milestone\n" + \
                      "Add test for git.Log"

    def test_grepString(self):
        log = git.Log(path="946b5ac..cfa1271",
                grep="test for git.Log",
                pretty="format:%s")
        res = log.output()
        assert res == "Add test for git.Log"
