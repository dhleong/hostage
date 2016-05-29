
import re

from ..core import RegexFilter

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
