
from typing import List

from logging import Logger
from logging import getLogger

from github import BadCredentialsException
from github import Github
from github.Milestone import Milestone
from github.PaginatedList import PaginatedList
from github.Repository import Repository

RepositoryNames = List[str]
MilestoneTitles = List[str]
IssueTitles     = List[str]


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

        repoNames: RepositoryNames = []

        userName: str = self._userName
        query:    str = f'user:{userName}'

        repos: PaginatedList = self._github.search_repositories(query=query)

        try:
            repoNames: RepositoryNames = []
            for repository in repos:
                repoNames.append(repository.full_name)

        except BadCredentialsException as e:
            self.logger.error(f'{e=}')
            self.__handleAuthenticationError()
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

    def getIssueTitles(self, repoName: str, milestoneTitle: str) -> IssueTitles:

        repo:        Repository    = self._github.get_repo(repoName)
        open_issues: PaginatedList = repo.get_issues(state=GithubAdapter.OPEN_ISSUE_INDICATOR)

        issueTitles: IssueTitles = []

        if milestoneTitle == GithubAdapter.ALL_ISSUES_INDICATOR:
            for issue in open_issues:
                issueTitles.append(issue.title)
        else:
            for issue in open_issues:
                mileStone: Milestone = issue.milestone
                if mileStone is not None and mileStone.title == milestoneTitle:
                    issueTitles.append(issue.title)

        return issueTitles

    def __handleAuthenticationError(self):
        pass
