
from ..core import Evaluator
from .base import Execute

class Tag(Evaluator):

    def __init__(self, name):
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

    def push(self, remote, force=False):
        args = ["git", "push", remote, self.name]

        if force:
            args.append("--force")

        return Execute(args).succeeds()

class Log(Execute):

    def __init__(self, path, grep=[], invertGrep=False, pretty=None):
        super(Log, self).__init__(\
                Log._toCli(path, grep, invertGrep, pretty))

    @staticmethod
    def _toCli(path, grep, invertGrep, pretty):
        args = ["git", "log", path]

        if isinstance(grep, basestring):
            for item in grep:
                args.append(\
                        "--grep=" + item.replace("#", "\#"))
        elif grep:
            args.append("--grep=" + grep.replace("#", "\#"))

        if invertGrep:
            args.append("--invert-grep")

        if pretty:
            args.append("--pretty=" + pretty)

        return args
