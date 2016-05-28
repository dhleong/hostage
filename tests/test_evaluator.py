#!/usr/bin/env py.test

import sys
import pytest

from hostage.core import verify, Result
from hostage.evaluator import Evaluator

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


def test_raw():
    r = SimpleEvaluator().succeed("Serenity")
    assert r == "Serenity"

def test_toVerifier():
    r = verify(SimpleEvaluator()).succeed("Serenity")
    assert isinstance(r, Result)
    assert r.value == "Serenity"

def test_toDryRun(argv, capsys):
    argv.append("--dryrun")
    r = verify(SimpleEvaluator()).succeed("Serenity")
    assert isinstance(r, Result)
    assert r.value == True

    out, _ = capsys.readouterr()
    assert out == "* DRYRUN: SimpleEvaluator.succeed('Serenity')\n"
