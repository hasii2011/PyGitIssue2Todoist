
from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from gittodoistclone.adapters.TodoistAdapter import TodoistAdapter
from gittodoistclone.adapters.TodoistAdapter import CloneInformation
from gittodoistclone.general.Preferences import Preferences

from tests.TestTodoistAdapterBase import TestTodoistAdapterBase


class TestTodoistAdapterReal(TestTodoistAdapterBase):
    """
    This unit test uses real credentials to test the todoist adapter.
    """
    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestTodoistAdapterBase.setUpClass()
        TestTodoistAdapterReal.clsLogger = getLogger(__name__)

        Preferences.determinePreferencesLocation()

    def setUp(self):

        self.logger: Logger = TestTodoistAdapterReal.clsLogger
        super().setUp()

    def tearDown(self):
        pass

    def testRealAPI(self):

        ci: CloneInformation = CloneInformation()
        ci.repositoryTask    = 'MockUser/MockRepo'
        ci.milestoneNameTask = 'MockMilestone'
        ci.tasksToClone      = ['TaskOpie', 'TaskGabby10Meows', 'TaskFranny']

        preferences: Preferences = Preferences()
        adapter: TodoistAdapter = TodoistAdapter(apiToken=preferences.todoistApiToken)

        adapter.createTasks(info=ci, progressCb=self._sampleCallback)


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestTodoistAdapterReal))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
