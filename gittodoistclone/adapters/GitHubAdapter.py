from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import cast

from logging import Logger
from logging import getLogger

from github import Github
from github import BadCredentialsException

from github.Issue import Issue
from github.Milestone import Milestone
from github.PaginatedList import PaginatedList
from github.Repository import Repository

from gittodoistclone.adapters.AdapterAuthenticationError import AdapterAuthenticationError

RepositoryNames = List[str]
MilestoneTitles = List[str]


@dataclass
class AbbreviatedGitIssue:

    issueTitle:   str = ''
    issueHTMLURL: str = ''


AbbreviatedGitIssues = List[AbbreviatedGitIssue]


class GithubAdapter:

    ALL_ISSUES_INDICATOR:     str = 'All'
    OPEN_MILESTONE_INDICATOR: str = 'Open'
    OPEN_ISSUE_INDICATOR:     str = 'open'

    def __init__(self, userName: str, authenticationToken: str):

        self.logger: Logger = getLogger(__name__)

        self._userName:            str    = userName
        self._authenticationToken: str    = authenticationToken
        self._github:              Github = Github(self._authenticationToken)

    def getRepositoryNames(self) -> RepositoryNames:

        userName: str = self._userName
        query:    str = f'user:{userName}'

        repos: PaginatedList = self._github.search_repositories(query=query)

        try:
            repoNames: RepositoryNames = []
            for repository in repos:
                repoNames.append(repository.full_name)

        except BadCredentialsException as e:
            self.logger.error(f'{e=}')
            raise AdapterAuthenticationError(e)

        return repoNames

    def getMileStoneTitles(self, repoName: str) -> MilestoneTitles:
        """
        Args:
            repoName: The repository name
        """

        repo:            Repository    = self._github.get_repo(repoName)
        mileStones:      PaginatedList = repo.get_milestones(state=GithubAdapter.OPEN_MILESTONE_INDICATOR)

        mileStoneTitles: MilestoneTitles = [GithubAdapter.ALL_ISSUES_INDICATOR]

        for mileStone in mileStones:
            mileStoneTitles.append(mileStone.title)

        return mileStoneTitles

    def getAbbreviatedIssues(self, repoName: str, milestoneTitle: str) -> AbbreviatedGitIssues:
        """
        Given a repo name and a milestone title return a simplified list of Git issues

        Args:
            repoName:       The Github repository name
            milestoneTitle: The milestone title that we filter on

        Returns:
            A list of abbreviated Git issues
        """

        repo:        Repository      = self._github.get_repo(repoName)
        openGitIssues: PaginatedList = repo.get_issues(state=GithubAdapter.OPEN_ISSUE_INDICATOR)

        simpleGitIssues: AbbreviatedGitIssues = []

        if milestoneTitle == GithubAdapter.ALL_ISSUES_INDICATOR:
            for openIssue in openGitIssues:
                simpleGitIssues.append(self._createAbbreviatedGitIssue(openIssue))
        else:
            for openIssue in openGitIssues:
                fullGitIssue: Issue = cast(Issue, openIssue)
                mileStone: Optional[Milestone] = fullGitIssue.milestone
                if mileStone is not None and mileStone.title == milestoneTitle:
                    simpleGitIssues.append(self._createAbbreviatedGitIssue(fullGitIssue))

        return simpleGitIssues

    def _createAbbreviatedGitIssue(self, fullGitIssue: Issue) -> AbbreviatedGitIssue:

        simpleIssue: AbbreviatedGitIssue = AbbreviatedGitIssue()

        simpleIssue.issueTitle   = fullGitIssue.title
        simpleIssue.issueHTMLURL = fullGitIssue.html_url

        return simpleIssue