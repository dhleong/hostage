
import re

from .base import Execute, File
from ..core import Evaluator, RegexFilter

class Gradle(Evaluator):

    def __init__(self, exe=None, silent=False):
        super(Gradle, self).__init__(exe, silent)
        self.exe = self._pickExe(exe)
        self.silent = silent

    def executes(self, *args):
        exe = Execute(*args)
        exe.params.insert(0, self.exe)
        return exe.succeeds(silent=self.silent)

    def hasLocalWrapper(self):
        return self.exe == './gradlew'

    def _pickExe(self, provided):
        if provided: return provided

        # TODO windows?
        if File('./gradlew').exists():
            return './gradlew'

        return 'gradle'

class Def(RegexFilter):
    """A filter that finds the value of a `def` statement
    """

    def __init__(self, varName):
        super(Def, self).__init__( \
                "%s\\s*=\\s*(.*)" % varName)

    def run(self, value):
        base = super(Def, self).run(value)

        # strip quotes for string values
        if base[0] in ['"', "'"]:
            return base[1:-1]
        else:
            return base
