#!/usr/bin/env py.test
#
# Git class tests
#

import os

from hostage.evaluators import git


def isShallowClone():
    return os.path.exists(os.path.join(git.Repo().root(), '.git/shallow'))


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
        assert date.hour == 19
        assert date.minute == 30
        assert date.tzinfo is not None

    def test_fromCommitish(self):
        tag = git.Tag.on('08d03e3')
        assert tag is not None
        assert tag.name == '0.6.0'

    def test_fromCommitish_404(self, capfd):
        tag = git.Tag.on('13f7f07')
        assert tag is None

        # no garbage output:
        out, err = capfd.readouterr()
        assert not out
        assert not err

    def test_latest(self):
        # pick a specific branch to ensure travis doesn't
        #  have a fit
        branch = git.Repo().branch()
        if not branch:
            # NOTE: when travis runs for a release tag,
            # it won't have the `master` branch. So, we
            # can just use HEAD
            branch = 'HEAD'

        tag = git.Tag.latest(filter="0.3.*", branch=branch)
        assert tag is not None
        assert tag.name == "0.3.0"


class TestLog:
    def test_output(self):
        if isShallowClone():
            # we can't properly run this test with a shallow clone (eg: travis)
            # TODO: can we rewrite these to somehow work on shallow clones?
            return

        log = git.Log(path="946b5ac..3dd3811", pretty="format:- %s")
        res = log.output()
        assert res == "- Convert git stuff to new Evaluator"

    def test_grepList(self):
        if isShallowClone():
            # we can't properly run this test with a shallow clone (eg: travis)
            return

        log = git.Log(path="946b5ac..cfa1271",
                grep=["test for git.Log", "github milestone"],
                pretty="format:%s")
        res = log.output()
        assert res == "Support editing github milestone\n" + \
                      "Add test for git.Log"

    def test_grepString(self):
        if isShallowClone():
            # we can't properly run this test with a shallow clone (eg: travis)
            return

        log = git.Log(path="946b5ac..cfa1271",
                grep="test for git.Log",
                pretty="format:%s")
        res = log.output()
        assert res == "Add test for git.Log"
