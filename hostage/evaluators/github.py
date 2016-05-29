
from __future__ import absolute_import

import os

from github import Github

from . import git
from .base import File
from ..core import Evaluator, RegexFilter

class Config:
    """Reusable config object"""

    def __init__(self, repo=None, token=None):
        self.repoName = repo
        self.token = token
        self._root = None
        self._repo = None

        if not self.repoName:
            self.repoName = self._determineRepo()
        if not self.repoName:
            raise Exception("Could not determine repo")

        if not self.token:
            self.token = self._determineToken()
        if not self.token:
            raise Exception("Could not determine token")

        self.gh = Github(self.token)

    def repo(self):
        if self._repo: return self._repo

        self._repo = self.gh.get_repo(self.repoName)
        return self._repo

    def _determineRepo(self):
        root = git.Repo().root()
        if not root:
            return
        self._root = root

        # TODO github enterprise?
        gitConfig = File(root + "/.git/config")
        f = RegexFilter("github.com:(.*)\.git")
        return gitConfig.filtersTo(f)

    def _determineToken(self):
        # environment var?
        token = os.environ.get("GITHUB_TOKEN")
        if token: return token

        # local path?
        if self._root:
            token = File(self._root + "/.github.token")\
                    .contents()
            if token: return token

        # hub?
        f = RegexFilter("oauth_token: (.*)")
        token = File("~/.config/hub").filtersTo(f)
        if token: return token

        # hubr?
        f = RegexFilter("TOKEN=[\"]?([^\"]+)[\"]?")
        token = File("~/.hubrrc").filtersTo(f)
        if token: return token


class _GHItem(Evaluator):
    def __init__(self, config, *params):
        super(_GHItem, self).__init__(*params)

        if config:
            self.config = config
        else:
            self.config = Config()

        self.gh = config.gh

class Milestone(_GHItem):
    def __init__(self, name, id=None, config=None):
        super(Milestone, self).__init__(config, name)

        self.name = name
        self.id = id

    def exists(self):
        return self._getId() is not None

    def _getId(self):
        if self.id == False: return None
        elif self.id: return self.id

        allMs = self.config.repo().get_milestones()
        ms = [m for m in allMs if m.title == self.name]
        if not len(ms):
            # couldn't find the milestone
            self.id = False
            return None

        self.id = ms[0]
        return self.id
