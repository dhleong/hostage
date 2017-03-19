#
# Basic functions
#

import os.path
import subprocess

from ..core import Evaluator, Filter


def _hasAg():
    # TODO we should probably cache this result:
    try:
        subprocess.check_output(["which", "ag"])
        return True
    except:
        return False


class File(Evaluator):

    def __init__(self, path):
        super(File, self).__init__(path)
        self.path = os.path.expanduser(path)

    def contents(self):
        if self.exists():
            with open(self.path) as fp:
                return fp.read()

    def delete(self):
        """Returns True if we were deleted, else
        False if we didn't exist in the first place
        """
        if self.exists():
            os.remove(self.path)
            return True
        return False

    def exists(self):
        return os.path.exists(self.path)

    def filtersTo(self, theFilter):
        if not isinstance(theFilter, Filter):
            raise Exception("%s is not a Filter" % theFilter)

        contents = self.contents()
        if not contents:
            return None

        return theFilter.run(self.contents())


class Execute(Evaluator):

    def __init__(self, *params, **kwargs):
        """Evaluator for executing something
        in the shell.

        :*params: If a single string, will be
        split up by spaces. For more complicated
        commands, pass as an array
        """
        super(Execute, self).__init__(*params)
        if len(params) == 1 and isinstance(params[0], basestring):
            self.params = params[0].split(" ")
        elif len(params) == 1 and type(params[0]) is list:
            self.params = params[0]
        else:
            self.params = list(params)
        self.kwargs = kwargs

    def output(self, errToOut=False):
        """Capture the output of a successful call,
        else return False
        """
        try:
            if errToOut:
                self.kwargs['stderr'] = subprocess.STDOUT
            return subprocess.check_output(self.params,
                    **self.kwargs)
        except subprocess.CalledProcessError:
            return False

    def succeeds(self, silent=True):
        """Ensure an exit code of 0. If silent=True,
        the output will be suppressed.
        """
        try:
            if silent:
                subprocess.check_output(self.params,
                        **self.kwargs)
            else:
                subprocess.check_call(self.params,
                        **self.kwargs)
            return True
        except subprocess.CalledProcessError:
            return False


class Grep(Execute):

    def __init__(self, text, inDir="."):
        """Executes grep (or `ag`, if available),
        and returns the output.
        """
        if _hasAg():
            super(Grep, self).__init__("ag", text, inDir)
        else:
            super(Grep, self).__init__("grep", "-R", text, inDir)

    def foundAny(self, silent=True):
        """Returns True if any matching text was found.
        If silent=False, the found text will not be suppressed
        """
        return self.succeeds(silent)
