from dataclasses import field
from typing import List
from typing import NewType
from typing import Optional
from typing import cast

from dataclasses import dataclass

from logging import Logger
from logging import getLogger

from github import Github
from github import BadCredentialsException

from github.Issue import Issue
from github.Milestone import Milestone
from github.Label import Label
from github.PaginatedList import PaginatedList
from github.Repository import Repository

from pygitissue2todoist.adapters.AdapterAuthenticationError import AdapterAuthenticationError
from pygitissue2todoist.adapters.GitHubConnectionError import GitHubConnectionError
from pygitissue2todoist.adapters.GitHubGeneralError import GitHubGeneralError

RepositoryNames = NewType('RepositoryNames', List[str])
MilestoneTitles = NewType('MilestoneTitles', List[str])


def createLabelsFactory() -> List[str]:
    return []


@dataclass
class AbbreviatedGitIssue:

    issueTitle:   str = ''
    issueHTMLURL: str = ''
    body:         str = ''
    prefix:       str = ''
    labels:       List[str] = field(default_factory=createLabelsFactory)


AbbreviatedGitIssues = NewType('AbbreviatedGitIssues', List[AbbreviatedGitIssue])


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

        # noinspection PyPackageRequirements
        import urllib3.exceptions

        try:
            repoNames: RepositoryNames = RepositoryNames([])
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

    def getMileStoneTitles(self, repoName: str) -> MilestoneTitles:
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

    def getAbbreviatedIssues(self, repoName: str, milestoneTitle: str) -> AbbreviatedGitIssues:
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
        simpleIssue.body         = fullGitIssue.body

        # Used to display the organization and repository name, in the Assigned To Me issue list
        try:
            simpleIssue.prefix = f"[{fullGitIssue.repository.organization.login}/{fullGitIssue.repository.name}]"
        except AttributeError:
            simpleIssue.prefix = f"[{fullGitIssue.repository.name}]"

        for label in fullGitIssue.labels:
            gitLabel: Label = cast(Label, label)
            simpleIssue.labels.append(gitLabel.name)

        return simpleIssue

    def getAssignedToMeIssues(self) -> AbbreviatedGitIssues:
        """
        Returns a list of issues assigned to the user.

        Equivalent to the following GitHub search:
        `gh search issues --assignee "@me" --include-prs`

        TODO: confirm how to include the PRs in the results
        `gh search issues --assignee "@me" --include-prs --state=open`
        """
        openGitIssues: PaginatedList = self._github.search_issues(
            query='assignee:@me state:open',
        )
        simpleGitIssues: AbbreviatedGitIssues = AbbreviatedGitIssues([])

        for openIssue in openGitIssues:
            simpleGitIssues.append(self._createAbbreviatedGitIssue(openIssue))

        return simpleGitIssues
