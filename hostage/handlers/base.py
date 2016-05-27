#
# Base handlers for hostage.py
#

from __future__ import print_function

from ..core import Handler

class echo(Handler):
    def __init__(self, *message):
        self.value = message

    def call(self, *args):
        self.do(*args)

    @staticmethod
    def do(*args):
        print(*args)

class echoAndDie(Handler):
    def __init__(self, message):
        self.value = message

    def call(self, *args):
        echo(*args).invoke()
        exit(1)

