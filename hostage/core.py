#
# Core, base classes for hostage.py
#

import sys
from abc import ABCMeta, abstractmethod
import inspect

from evaluator import Evaluator

class Result:

    def __init__(self, value=None):
        self.value = value;

    def orElse(self, handler):
        if not self.value:
            self._invoke(handler)

        # we return a bogus value so you can keep stringing along handlers with then()
        return Result("-bogus-")

    def then(self, handler):
        if self.value:
            self._invoke(handler)

        # we return a bogus value so you can keep stringing along handlers with then()
        return Result("-bogus-")

    def valueElse(self, handler):
        if self.value:
            return self.value

        return self.orElse(handler)

    def _invoke(self, handler):
        if inspect.isclass(handler):
            handler(self.value).invoke()
        elif inspect.isfunction(handler) or inspect.ismethod(handler):
            handler(self.value)
        else:
            handler.invoke(self.value)

class Handler:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.value = None

    def invoke(self, incoming=None):
        if self.value and isinstance(self.value, tuple):
            return self.call(*self.value)
        elif self.value:
            return self.call(self.value)
        else:
            return self.call(incoming)

    @abstractmethod
    def call(self, *args):
        pass

def verify(value):

    if isinstance(value, Evaluator):
        if "--dryrun" in sys.argv:
            return value._toDryVerifier(Result)

        else:
            return value._toVerifier(Result)
    else:
        return Result(value)
