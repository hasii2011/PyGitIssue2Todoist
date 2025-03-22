
from typing import cast

from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import PropertyMock
from unittest.mock import patch

from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssue
from pygitissue2todoist.adapters.GitHubAdapter import GithubAdapter
from pygitissue2todoist.adapters.GitHubAdapter import IssueOwner
from pygitissue2todoist.adapters.GitHubAdapter import MilestoneTitles
from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssues
from pygitissue2todoist.adapters.GitHubAdapter import Slug
from pygitissue2todoist.adapters.GitHubAdapter import Slugs
from pygitissue2todoist.general.Preferences import Preferences

from tests.ProjectTestBase import ProjectTestBase


class TestGithubAdapter(ProjectTestBase):

    TEST_REPOSITORY_NAME: Slug = Slug('hasii2011/StarTrekPy')
    TEST_MILESTONE_TITLE: str  = '0.7 Release'
    TEST_ISSUE_URL:       str  = 'https://www.ElderAbuseInTheWhiteHouse'

    clsLogger: Logger = cast(Logger, None)

    @classmethod
    def setUpClass(cls):
        ProjectTestBase.setUpLogging()
        TestGithubAdapter.clsLogger = getLogger(__name__)

    def setUp(self):

        self.logger: Logger = TestGithubAdapter.clsLogger

    def tearDown(self):
        pass

    def testGetRepositoryNames(self):

        githubAdapter: GithubAdapter = GithubAdapter(userName='mockUserName', authenticationToken='mockToken')

        githubAdapter._github = MagicMock()

        with patch('github.Repository.Repository') as mockRepo1:
            with patch('github.Repository.Repository') as mockRepo2:

                type(mockRepo1).full_name = PropertyMock(return_value='Mock/Repo1')
                type(mockRepo2).full_name = PropertyMock(return_value='Mock/Repo2')

                githubAdapter._github.search_repositories.return_value = [mockRepo1, mockRepo2]

                repoNames: Slugs = githubAdapter.getRepositoryNames()

                self.assertTrue(len(repoNames) == 2, "We should have found an exact number")

                for repoName in repoNames:
                    self.logger.info(f'{repoName=}')

    def testGetMilestones(self):

        githubAdapter: GithubAdapter = GithubAdapter(userName='mockUserName', authenticationToken='mockToken')
        githubAdapter._github = Mock()

        with patch('github.Milestone.Milestone') as mockMileStone1:
            with patch('github.Milestone.Milestone') as mockMileStone2:

                type(mockMileStone1).title = PropertyMock(return_value='MockMilestone1')
                type(mockMileStone2).title = PropertyMock(return_value='MockMilestone2')

                mockRepo = Mock()
                mockRepo.get_milestones.return_value = [mockMileStone1, mockMileStone2]

                githubAdapter._github.get_repo.return_value = mockRepo
                #
                # Finally got all the mocks set up
                #
                milestones: MilestoneTitles = githubAdapter.getMileStoneTitles(TestGithubAdapter.TEST_REPOSITORY_NAME)

                self.assertTrue(len(milestones) != 0, "We should have found some milestones")

                for ms in milestones:
                    self.logger.info(f'{ms=}')

    def testGetIssues(self):

        githubAdapter: GithubAdapter = GithubAdapter(userName='mockUserName', authenticationToken='mockToken')
        githubAdapter._github = Mock()

        mockRepo = Mock()

        with patch('github.Issue.Issue') as mockIssue1:
            with patch('github.Milestone.Milestone') as mockMileStone1:

                type(mockMileStone1).title = PropertyMock(return_value=TestGithubAdapter.TEST_MILESTONE_TITLE)

                type(mockIssue1).title = PropertyMock(return_value='MockIssue1')
                type(mockIssue1).html_url = PropertyMock(return_value=TestGithubAdapter.TEST_ISSUE_URL)
                type(mockIssue1).milestone = PropertyMock(return_value=mockMileStone1)

                githubAdapter._github.get_repo.return_value = mockRepo

                mockRepo.get_issues.return_value = [mockIssue1]
                #
                # Done patching
                #
                simpleGitIssues: AbbreviatedGitIssues = githubAdapter.getAbbreviatedIssues(TestGithubAdapter.TEST_REPOSITORY_NAME,
                                                                                           TestGithubAdapter.TEST_MILESTONE_TITLE)
                self.assertTrue(len(simpleGitIssues) != 0, "We should have found some open issues")

                for issueTitle in simpleGitIssues:
                    self.logger.info(f'{issueTitle=}')

    def testGetIssuesAssignedToOwner(self):

        preferences: Preferences = Preferences()

        githubAdapter: GithubAdapter = GithubAdapter(userName=preferences.gitHubUserName,
                                                     authenticationToken=preferences.gitHubAPIToken)

        # noinspection SpellCheckingInspection
        slugs: Slugs = Slugs(
            [
                Slug('hasii2011/pyut'),
                Slug('hasii2011/pytrek'),
                Slug('hasii2011/pyutmodel'),
                Slug('hasii2011/CodeSigningScripts'),
                Slug('hasii2011/Chip8Emulator'),
                Slug('hasii2011/albow-python-3'),
            ]
        )

        issueOwner: IssueOwner = IssueOwner(preferences.gitHubUserName)
        simpleGitIssues: AbbreviatedGitIssues = githubAdapter.getIssuesAssignedToOwner(slugs, issueOwner=issueOwner, callback=self._statusCallback)

        print(f'Retrieved a total of {len(simpleGitIssues)} issues')

    def testActuallyAssignedToOwner(self):
        preferences: Preferences = Preferences()

        githubAdapter: GithubAdapter = GithubAdapter(userName=preferences.gitHubUserName,
                                                     authenticationToken=preferences.gitHubAPIToken)

        # noinspection SpellCheckingInspection
        slugs: Slugs = Slugs(
            [
                Slug('hasii2011/TestRepository'),
            ]
        )

        issueOwner: IssueOwner = IssueOwner(preferences.gitHubUserName)
        simpleGitIssues: AbbreviatedGitIssues = githubAdapter.getIssuesAssignedToOwner(slugs, issueOwner=issueOwner, callback=self._statusCallback)

        for issue in simpleGitIssues:
            simpleIssue: AbbreviatedGitIssue = cast(AbbreviatedGitIssue, issue)

            self.assertNotEqual('Not Assigned To Me', simpleIssue.issueTitle, 'Should not get this one')

    def _statusCallback(self, msg: str):
        print(f'{msg}')


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()

    testSuite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestGithubAdapter))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
