#!/usr/bin/env py.test
#
# Core class tests
#

from hostage.evaluators.base import *

class TestFile:
    def test_exists(self, tmpdir):
        f = tmpdir.join("foo")
        f.write("bar")
        fEval = File(str(f.realpath()))
        assert fEval.exists() == True

    def test_notExists(self):
        res = File("foo")
        assert res.exists() == False

    def test_contents(self, tmpdir):
        f = tmpdir.join("foo")
        f.write("bar")
        fEval = File(str(f.realpath()))
        assert fEval.contents() == "bar"

    def test_noContents(self, tmpdir):
        fEval = File("foo")
        assert fEval.contents() is None

class TestExecute:
    def test_initWithString(self):
        assert Execute("foo bar").params == ['foo', 'bar']

    def test_initWithVargs(self):
        assert Execute("foo", "bar").params == ['foo', 'bar']
    def test_initWithList(self):
        assert Execute(["foo", "bar"]).params == ['foo', 'bar']

    def test_succeeds(self):
        result = Execute("echo hi").succeeds()
        assert result == True

        result = Execute("echo hi").succeeds(silent=True)
        assert result == True

    def test_output(self):
        result = Execute("echo hi").output()
        assert result == "hi\n"

class TestGrep:
    def test_foundAny(self):
        result = Grep("test").foundAny()
        assert result == True
