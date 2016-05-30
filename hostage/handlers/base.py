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

class die(Handler):

    """Exit with error code (defaults to 1)"""

    def __init__(self, errorCode=1):
        self.value = errorCode

    def call(self, *args):
        exit(args[0])

class echoAndDie(Handler):
    def __init__(self, message):
        self.value = message

    def call(self, *args):
        echo(*args).invoke()
        exit(1)

