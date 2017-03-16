
import dateutil.parser

from ..core import Evaluator
from .base import Execute


class Tag(Evaluator):

    def __init__(self, name):
        super(Tag, self).__init__(name)
        self.name = name

    def create(self, force=False):
        args = ["git", "tag"]

        if force:
            args.append("--force")

        args.append(self.name)
        return Execute(args).succeeds()

    def delete(self):
        return Execute("git", "tag", "-d", self.name).succeeds()

    def exists(self):
        exe = Execute("git", "tag", "-l", self.name)
        return len(exe.output()) > 0

    def get_created_date(self):
        exe = Execute("git", "log", "-1",
                "--format=%ai",  # author-created date in iso-ish format
                self.name)       # (note: travis doesn't have iso-strict)
        dateString = exe.output()
        if len(exe.output()) > 0:
            return dateutil.parser.parse(dateString)

    def push(self, remote, force=False):
        args = ["git", "push", remote, self.name]

        if force:
            args.append("--force")

        return Execute(args).succeeds()


class Log(Execute):

    def __init__(self, path, grep=[], invertGrep=False, pretty=None):
        super(Log, self).__init__(
            Log._toCli(path, grep, invertGrep, pretty))

    @staticmethod
    def _toCli(path, grep, invertGrep, pretty):
        args = ["git", "log", path]

        if isinstance(grep, basestring):
            args.append("--grep=" + grep.replace("#", "\#"))
        elif type(grep) is list:
            for item in grep:
                args.append(
                    "--grep=" + item.replace("#", "\#"))
        else:
            raise Exception("Unexpected arg for grep: %s" % repr(grep))

        if invertGrep:
            args.append("--invert-grep")

        if pretty:
            args.append("--pretty=" + pretty)

        return args


class Repo(Evaluator):

    """Git Repo Utilities"""

    def root(self):
        path = Execute("git rev-parse --show-toplevel").output()
        if path:
            return path.strip()
