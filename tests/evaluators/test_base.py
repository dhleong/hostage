#!/usr/bin/env py.test
#
# Core class tests
#

from hostage.evaluators.base import *

class TestExecute:
    def test_success(self):
        res = execute("echo", "hi")
        assert res.value == "hi\n"

    def test_error(self):
        res = execute("which", "no-existent-program")
        assert not res.value


class TestExecStatus:
    def test_success(self):
        res = execStatus("echo", "hi")
        assert res.value == True

    def test_error(self):
        res = execStatus("which", "no-existent-program")
        assert not res.value


class TestFindFile:
    def test_success(self, tmpdir):
        f = tmpdir.join("foo")
        f.write("bar")
        res = findFile(str(f.realpath()))
        assert res.value == True

    def test_success(self):
        res = findFile("foo")
        assert res.value == False
