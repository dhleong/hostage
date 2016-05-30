
import os
import subprocess

from ..core import Evaluator
from .base import File

class Edit(Evaluator):
    """Open a file for editing and block until finished.
    Tries to use $EDITOR
    """

    def __init__(self, theFile, withContent=None):
        super(Edit, self).__init__(theFile, withContent)

        self.content = withContent

        if isinstance(theFile, File):
            self.theFile = theFile
        else:
            self.theFile = File(theFile)

    def didCreate(self):
        """Open the file, block until done, and return
        True if the file was created. This does NOT
        verify that it did not exist before, merely
        that it does exist *now*.
        """

        self._await()
        return self.theFile.exists()

    def _await(self):
        editor = os.environ.get("EDITOR", "vim")
        if editor[-3:].lower() == "vim":
            self._vim(editor)
        else:
            raise Exception("Unsupported editor `%s`" % editor)

    def _vim(self, exe="vim"):
        args = [exe]

        env = os.environ.copy()

        if self.content:
            args.append("-c")
            args.append("silent put =$NOTES_CONTENT")

            env["NOTES_CONTENT"] = self.content

        args.append(self.theFile.path)
        e = subprocess.call(args, env=env)

        return e == 0
