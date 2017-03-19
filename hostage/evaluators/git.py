
import dateutil.parser

from ..core import Evaluator, Filter
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

    @staticmethod
    def latest(filter=None, branch="master", searchDepth=10):
        """Get the most recent Tag on the given branch; useful for
        grabbing all commit logs between now and the last release,
        for example. You may optionally provide a Filter to
        restrict the possible candidates"""
        commitsRaw = Execute("git", "rev-list", branch, "--tags",
                "--max-count=%d" % searchDepth).output()
        if not commitsRaw: return None

        commits = [c for c in commitsRaw.split("\n") if c]
        tagNames = Execute(["git", "describe", "--tags"] +
                commits).output()
        if not tagNames: return None
        tagNames = [t for t in tagNames.split("\n") if t]

        if not filter:
            # no pattern? just the very first
            return Tag(tagNames[0])

        filter = Filter.wrap(filter)
        for tagName in tagNames:
            if filter.run(tagName):
                return Tag(tagName)


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

    def branch(self):
        branch = Execute("git rev-parse --abbrev-ref HEAD").output()
        if branch and not branch.startswith('HEAD'):
            return branch.strip()
