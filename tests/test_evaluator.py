#!/usr/bin/env py.test

import sys
import pytest

from hostage.core import verify, Result
from hostage.evaluator import Evaluator
from hostage import File

class SimpleEvaluator(Evaluator):

    def succeed(self, val):
        return val

@pytest.fixture
def argv(request):
    original = list(sys.argv)
    def fin():
        # restore the original argv
        sys.argv[:] = original

    request.addfinalizer(fin)
    return sys.argv

@pytest.fixture
def dryrun(argv):
    argv.append('--dryrun')

def test_raw():
    r = SimpleEvaluator().succeed("Serenity")
    assert r == "Serenity"

def test_toVerifier():
    r = verify(SimpleEvaluator()).succeed("Serenity")
    assert isinstance(r, Result)
    assert r.value == "Serenity"

def test_toDryRun(dryrun, capsys):
    r = verify(SimpleEvaluator()).succeed("Serenity")
    assert isinstance(r, Result)
    assert r.value == True

    out, _ = capsys.readouterr()
    assert out == "* DRYRUN: SimpleEvaluator().succeed('Serenity')\n"


class TestVerifyBase:
    """Some quick tests to check verify() in "real world"
    scenarios, with actual Evaluators (though they have
    their own implementation unit tests as well)
    """

    def test_dryRun_File(self, dryrun, capsys):
        r = verify(File("foo")).exists()
        assert r.value == True

        out, _ = capsys.readouterr()
        assert out == "* DRYRUN: File('foo').exists()\n"
