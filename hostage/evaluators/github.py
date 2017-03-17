#
# Github actions
#


from __future__ import absolute_import

import os
from urllib import urlencode

from github import Github, Label

from . import git
from .base import File
from .http import Http
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
            token = File(self._root + "/.github.token").contents()
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

        self.gh = self.config.gh


class Issue(_GHItem):
    def __init__(self, number, config=None, inst=None):
        super(Issue, self).__init__(config, number)
        self.number = number
        self._inst = inst

    def exists(self):
        return self._getInst() is not None

    def _getInst(self):
        if self._inst: return self._inst
        inst = self.config.repo().get_issue(self.number)
        self._inst = inst
        return inst

    def __getattr__(self, attr):
        if attr == 'labels':
            # lazy-inflate labels
            self.labels = [label.name for label in self._getInst().labels]
            return self.labels

        return getattr(self._getInst(), attr)


class Milestone(_GHItem):
    def __init__(self, name, id=None, config=None):
        super(Milestone, self).__init__(config, name)

        self.name = name
        self.id = id
        self._inst = None

    def exists(self):
        return self._getInst() is not None

    def edit(self, **kwargs):
        """Edit the milestone

        :title: string New title
        :state: string "open" or "closed"
        :description: string
        :due_on: date

        """
        inst = self._getInst()
        if not inst: return None

        if 'title' not in kwargs:
            kwargs['title'] = self.name

        inst.edit(**kwargs)

        return True

    def _getInst(self):
        if self._inst: return self._inst
        if self.id:
            inst = self.config.repo().get_milestone(self.id)
            self._inst = inst
            return inst
        self._getId()
        return self._inst

    def _getId(self):
        if self.id is False: return None
        elif self.id: return self.id

        allMs = self.config.repo().get_milestones()
        ms = [m for m in allMs if m.title == self.name]
        if not len(ms):
            # couldn't find the milestone
            self.id = False
            return None

        self._inst = ms[0]
        self.id = ms[0].number
        return self.id


class Release(_GHItem):

    """Update a Github Release"""

    def __init__(self, tag, config=None, http=None):
        """TODO: to be defined1.

        :tag: Name of the tag for the release
        :config: TODO

        """
        super(Release, self).__init__(config, tag)

        self.tag = tag
        self._inst = None

        if http is None:
            self._http = Http()
        else:
            self._http = http

    def create(self, name=None, body=None, draft=False, prerelease=False):
        """Create the release

        :name: string
        :body: string Text describing the contents of the tag
        :draft: bool True to create an "unpublished" release
        :prerelease: bool True to identify as "pre-release"
        :returns: TODO

        """
        if name is None:
            name = self.tag

        self._inst = self.config.repo().create_git_release(
            self.tag,
            name,
            body,
            draft,
            prerelease)

        return True

    def exists(self):
        return self._getInst() is not None

    def uploadFile(self, path, contentType, label=None):
        """TODO: Docstring for uploadFile.

        :path: TODO
        :contentType: TODO
        :label: TODO
        :returns: TODO

        """
        asFile = File(path)
        if not asFile.exists():
            return False
        path = asFile.path

        inst = self._getInst()
        if not inst: return None

        uploadUrl = inst.upload_url
        uploadUrl = uploadUrl[0:uploadUrl.find('{')]

        params = {'name': os.path.basename(path)}
        if label is not None:
            params['label'] = label

        uploadUrl += '?' + urlencode(params)

        with open(path, 'rb') as fileData:
            return self._http.post(uploadUrl,
                    body=fileData,
                    headers={
                        'Authorization': 'token %s' % self.config.token,
                        'Content-Type': contentType})

        return False

    def _getInst(self):
        if self._inst: return self._inst
        inst = self.config.repo().get_release(self.tag)
        self._inst = inst
        return inst


def _toLabel(labelOrString):
    if isinstance(labelOrString, Label.Label):
        return labelOrString

    # minor hacks to avoid unnecessary network calls:
    return Label.Label(requester=None, headers=None, completed=True,
            attributes={'name': labelOrString})


def find_issues(config=None, **kwargs):
    """Search for issues. Valid keyword parameters:
    - milestone: a github.Milestone instance
    - state: "open" or "closed"
    - assignee: username
    - labels: list of string label names
    - sort: string
    - direction: string
    - since: datetime.datetime
    """
    # convert our Milestone into a PyGithub Milestone
    if 'milestone' in kwargs:
        m = kwargs['milestone']
        if isinstance(m, Milestone):
            kwargs['milestone'] = m._getInst()

    # convert string labels into PyGithub Labels
    if 'labels' in kwargs:
        labels = kwargs['labels']
        kwargs['labels'] = [_toLabel(l) for l in labels]

    found = _GHItem(config).config.repo().get_issues(**kwargs)
    return [Issue(issue.number, config=config, inst=issue)
            for issue in found]
