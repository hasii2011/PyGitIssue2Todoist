
from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from gittodoistclone.general.Preferences import Preferences

from gittodoistclone.adapters.GithubAdapter import GithubAdapter
from gittodoistclone.adapters.GithubAdapter import RepositoryNames
from gittodoistclone.adapters.GithubAdapter import MilestoneTitles
from gittodoistclone.adapters.GithubAdapter import IssueTitles

from tests.TestBase import TestBase


class TestGithubAdapter(TestBase):

    TEST_REPOSITORY_NAME: str = 'hasii2011/StarTrekPy'
    TEST_MILESTONE_TITLE: str = '0.7 Release'

    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestGithubAdapter.clsLogger = getLogger(__name__)

    def setUp(self):

        self.logger: Logger = TestGithubAdapter.clsLogger

        Preferences.determinePreferencesLocation()

        preferences: Preferences = Preferences()

        self._githubAdapter: GithubAdapter = GithubAdapter(userName=preferences.githubUserName, authenticationToken=preferences.githubApiToken)

    def tearDown(self):
        pass

    def testGetRepositoryNames(self):

        repoNames: RepositoryNames = self._githubAdapter.getRepositoryNames()

        self.assertTrue(len(repoNames) != 0, "We should have found some repositories")

        for repoName in repoNames:
            self.logger.info(f'{repoName=}')

    def testGetMilestones(self):

        milestones: MilestoneTitles = self._githubAdapter.getMileStoneTitles(TestGithubAdapter.TEST_REPOSITORY_NAME)

        self.assertTrue(len(milestones) != 0, "We should have found some milestones")

        for ms in milestones:
            self.logger.info(f'{ms=}')

    def testGetIssues(self):

        issuesTitles: IssueTitles = self._githubAdapter.getIssueTitles(TestGithubAdapter.TEST_REPOSITORY_NAME, TestGithubAdapter.TEST_MILESTONE_TITLE)
        self.assertTrue(len(issuesTitles) != 0, "We should have found some open issues")

        for issueTitle in issuesTitles:
            self.logger.info(f'{issueTitle=}')


def suite() -> TestSuite:
    """You need to change the name of the test class here also."""
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestGithubAdapter))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
