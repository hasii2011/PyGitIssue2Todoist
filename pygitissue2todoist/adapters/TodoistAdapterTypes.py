
from typing import List

from dataclasses import dataclass
from dataclasses import field
from urllib.parse import urlparse, ParseResult

from pygitissue2todoist.general.GitHubURLOption import GitHubURLOption
from pygitissue2todoist.general.PreferencesV2 import PreferencesV2


@dataclass
class GitIssueInfo:
    gitIssueName: str = ''
    gitIssueURL:  str = ''
    _preferences: PreferencesV2 = PreferencesV2()

    def _verify_github_issue_url(self) -> ParseResult:
        """
        This performs some basic validation of the URL - eg that it looks like it point to a GitHub Issue or Pull Request.
        It only works by examining the URL in string form, not by actually making a request to the URL.
        """
        parsed_url = urlparse(self.gitIssueURL)

        try:
            assert parsed_url.scheme == 'https', f'Expected https scheme, got {parsed_url.scheme}'
            assert parsed_url.netloc == 'github.com', f'Expected github.com netloc, got {parsed_url.netloc}'
            assert len(parsed_url.path.split('/')) >= 2, f'Expected at least 2 path components, got {len(parsed_url.path.split("/"))}'
            print('{}'.format(parsed_url.path.split('/')))

            assert parsed_url.path.split('/')[0] == '', f'Expected path to start with "/", got {parsed_url.path.split("/")[0]}'
            assert parsed_url.path.split('/')[3] in ('issues', 'pull'), f'Expected path to include the word "issues" or "pull", got {parsed_url.path.split("/")[0]}'

            return parsed_url
        except AssertionError as ae:
            raise ValueError(f'Invalid GitHub Issue URL: {self.gitIssueURL}') from ae


    @property
    def github_repo_name(self) -> str:
        parsed_url = self._verify_github_issue_url()
        return parsed_url.path.split('/')[2]

    @property
    def github_org_name(self) -> str:
        parsed_url = self._verify_github_issue_url()
        return parsed_url.path.split('/')[1]


    def format_add_task_params(self) -> tuple[str, str, str]:
        option: GitHubURLOption = self._preferences.gitHubURLOption

        content: str = ''
        description: str = ''
        comment: str = ''

        match option:
            case GitHubURLOption.DoNotAdd:
                content=self.gitIssueName
            case GitHubURLOption.AddAsDescription:
                content=self.gitIssueName
                description=self.gitIssueURL
            case GitHubURLOption.AddAsComment:
                content=self.gitIssueName
                comment=self.gitIssueURL
                print(f'Comment added: {comment}')
            case GitHubURLOption.HyperLinkedTaskName:
                linkedTaskName: str = f'[{self.gitIssueName}]({self.gitIssueURL})'
                content=linkedTaskName
            case _:
                self.clsLogger.error(f'Unknown URL option: {option}')

        return content, description, comment



@dataclass
class CloneInformation:
    # TODO: Add hierarchy of orgs/repos/issues or milestones as fields here
    repositoryTask:    str = ''
    milestoneNameTask: str = ''
    tasksToClone:      List[GitIssueInfo] = field(default_factory=list)


@dataclass
class TaskDescription:
    """
    This class is used to store parameter for future calls to `todolist.add_task()`
    """
    content: str = ''
    description: str = ''
    comment: str = ''