
from typing import Callable
from typing import List
from typing import NewType
from typing import Optional
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass
from dataclasses import field

from github import Github
from github import BadCredentialsException
from github.Auth import Token
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from github.Milestone import Milestone
from github.Label import Label
from github.Issue import Issue

#
# Import the module because it appears that PyGithub dynamically loads it.  So
# while the code works when executed in the IDE, it does not work when I build
# Pyut as a standalone applications.  The noinspection comments I include because
# I despise warnings in the PyCharm IDE.  ;-)
#
# noinspection PyPackageRequirements
# noinspection PyUnresolvedReferences
from cffi import api


from pygitissue2todoist.adapters.AdapterAuthenticationError import AdapterAuthenticationError
from pygitissue2todoist.adapters.GitHubConnectionError import GitHubConnectionError
from pygitissue2todoist.adapters.GitHubGeneralError import GitHubGeneralError

MilestoneTitles = NewType('MilestoneTitles', List[str])
IssueOwner      = NewType('IssueOwner',      str)


def createLabelsFactory() -> List[str]:
    return []


@dataclass
class AbbreviatedGitIssue:

    slug:         str = ''
    issueTitle:   str = ''
    issueHTMLURL: str = ''
    body:         str = ''
    labels:       List[str] = field(default_factory=createLabelsFactory)


AbbreviatedGitIssues = NewType('AbbreviatedGitIssues', List[AbbreviatedGitIssue])

Slug  = NewType('Slug',  str)
Slugs = NewType('Slugs', List[Slug])

IssuesCallback = Callable[[str], None]


class GithubAdapter:

    ALL_ISSUES_INDICATOR:     str = 'All'
    OPEN_MILESTONE_INDICATOR: str = 'Open'
    OPEN_ISSUE_INDICATOR:     str = 'open'

    def __init__(self, userName: str, authenticationToken: str):

        self.logger: Logger = getLogger(__name__)

        self._userName:            str    = userName
        self._authenticationToken: str    = authenticationToken
        self._github:              Github = Github(auth=Token(self._authenticationToken))

    def getRepositoryNames(self) -> Slugs:

        userName: str = self._userName
        query:    str = f'user:{userName}'

        repos: PaginatedList = self._github.search_repositories(query=query)

        # noinspection PyPackageRequirements
        import urllib3.exceptions

        try:
            repoNames: Slugs = Slugs([])
            for repository in repos:
                repoNames.append(repository.full_name)

        except BadCredentialsException as e:
            self.logger.error(f'{e=}')
            raise AdapterAuthenticationError(e)
        # Can't figure out what kind of outer error this;  Use simplest
        except Exception as ge:
            self.logger.error(f'{ge}')
            args = ge.args
            if isinstance(args, tuple):
                self.logger.error(f'GitHub error:  {ge}')
                raise GitHubConnectionError(ge)
            else:
                reason = ge.args[0].reason
                self.logger.error(f'{reason=}')
                if isinstance(reason, urllib3.exceptions.NewConnectionError):
                    raise GitHubConnectionError(ge)

                raise GitHubGeneralError(ge)

        return repoNames

    def getMileStoneTitles(self, repoName: Slug) -> MilestoneTitles:
        """
        Args:
            repoName: The repository name
        """

        repo:            Repository    = self._github.get_repo(repoName)
        mileStones:      PaginatedList = repo.get_milestones(state=GithubAdapter.OPEN_MILESTONE_INDICATOR)

        mileStoneTitles: MilestoneTitles = MilestoneTitles([GithubAdapter.ALL_ISSUES_INDICATOR])

        for mileStone in mileStones:
            mileStoneTitles.append(mileStone.title)

        return mileStoneTitles

    def getAbbreviatedIssues(self, repoName: Slug, milestoneTitle: str) -> AbbreviatedGitIssues:
        """
        Given a repo name and a milestone title return a simplified list of Git issues

        Args:
            repoName:       The GitHub repository name
            milestoneTitle: The milestone title that we filter on

        Returns:
            A list of abbreviated Git issues
        """

        repo:        Repository      = self._github.get_repo(repoName)
        openGitIssues: PaginatedList = repo.get_issues(state=GithubAdapter.OPEN_ISSUE_INDICATOR)

        simpleGitIssues: AbbreviatedGitIssues = AbbreviatedGitIssues([])

        if milestoneTitle == GithubAdapter.ALL_ISSUES_INDICATOR:
            for openIssue in openGitIssues:
                simpleGitIssues.append(self._createAbbreviatedGitIssue(slug=repoName, fullGitIssue=openIssue))
        else:
            for openIssue in openGitIssues:
                fullGitIssue: Issue = cast(Issue, openIssue)
                mileStone: Optional[Milestone] = fullGitIssue.milestone
                if mileStone is not None and mileStone.title == milestoneTitle:
                    simpleGitIssues.append(self._createAbbreviatedGitIssue(slug=repoName, fullGitIssue=fullGitIssue))

        return simpleGitIssues

    def getIssuesAssignedToOwner(self, slugs: Slugs, issueOwner: IssueOwner, callback: IssuesCallback) -> AbbreviatedGitIssues:
        """
        Creates an abbreviated list open issues assigned to the issue owner

        Args:
            slugs:          GitHub Slugs;  e.g. 'hasii2011/pyut'
            issueOwner:     The ones we are looking for
            callback:       Status reporting callback

        Returns:  A list of issues assigned to the user.
        """
        simpleGitIssues: AbbreviatedGitIssues = AbbreviatedGitIssues([])

        for slug in slugs:
            repo:       Repository           = self._github.get_repo(slug)
            openIssues: PaginatedList[Issue] = repo.get_issues(state='open')

            issueCount: int = 0
            for issue in openIssues:
                potentialIssue: Issue = cast(Issue, issue)
                # TODO:  Might want to look through the assignees list also
                if potentialIssue.assignee is None:
                    pass
                elif potentialIssue.assignee.login == issueOwner:
                    simpleGitIssues.append(self._createAbbreviatedGitIssue(slug=slug, fullGitIssue=issue))
                    issueCount += 1

            msg: str = f'Retrieved {issueCount} issues from {slug}'
            callback(msg)

        return simpleGitIssues

    def _createAbbreviatedGitIssue(self, slug: Slug, fullGitIssue: Issue) -> AbbreviatedGitIssue:

        simpleIssue: AbbreviatedGitIssue = AbbreviatedGitIssue()

        simpleIssue.slug         = str(slug)
        simpleIssue.issueTitle   = fullGitIssue.title
        simpleIssue.issueHTMLURL = fullGitIssue.html_url
        simpleIssue.body         = fullGitIssue.body
        for label in fullGitIssue.labels:
            gitLabel: Label = cast(Label, label)
            simpleIssue.labels.append(gitLabel.name)

        return simpleIssue
