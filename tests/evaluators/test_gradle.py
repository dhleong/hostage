#!/usr/bin/env py.test
#
# Gradle class tests
#

from hostage import gradle

def test_DefFilter():
    res = gradle.Def("ship") \
            .run("manifest {\n  def ship = 'serenity'\n}")
    assert res == "serenity"

    res = gradle.Def("cap") \
            .run("manifest {\n  def cap = 20\n}")
    assert res == "20"
