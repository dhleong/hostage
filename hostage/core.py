#
# Core, base classes for hostage.py
#

import re
import sys
import inspect
from abc import ABCMeta, abstractmethod

from evaluator import Evaluator

class Result:

    def __init__(self, value=None):
        self.value = value;

    def orElse(self, handler):
        if not self.value:
            return self._invoke(handler)

    def then(self, handler):
        if self.value:
            self._invoke(handler)

        # we return the same value for correct chaining
        return Result(self.value)

    def valueElse(self, handler):
        if self.value:
            return self.value

        return self.orElse(handler)

    def _invoke(self, handler):
        if inspect.isclass(handler):
            return handler(self.value).invoke()
        elif inspect.isfunction(handler) or inspect.ismethod(handler):
            return handler(self.value)
        else:
            return handler.invoke(self.value)

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

class Filter:
    __metaclass__ = ABCMeta

    @abstractmethod
    def run(self, value):
        pass

class RegexFilter(Filter):
    def __init__(self, regex):
        self.regex = re.compile(regex)

    def run(self, value):
        m = self.regex.search(value)
        if m:
            return m.group(1)
