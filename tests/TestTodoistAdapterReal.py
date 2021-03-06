
from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from todoist.models import Project

from gittodoistclone.adapters.TodoistAdapter import ProjectDictionary
from gittodoistclone.adapters.TodoistAdapter import ProjectName
from gittodoistclone.adapters.TodoistAdapter import TodoistAdapter
from gittodoistclone.adapters.TodoistAdapter import CloneInformation

from gittodoistclone.general.Preferences import Preferences

from tests.TestTodoistAdapterBase import TestTodoistAdapterBase

NUMBER_OF_TEST_MILESTONE_TASKS: int = 2
NUMBER_OF_TEST_DEV_TASKS:       int = 4


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
        preferences: Preferences = Preferences()
        self._adapter: TodoistAdapter = TodoistAdapter(apiToken=preferences.todoistApiToken)

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

    def testGetCurrentProjects(self):

        adapter: TodoistAdapter = self._adapter

        projectDictionary: ProjectDictionary = adapter._getCurrentProjects()

        self.assertIsNotNone(projectDictionary, 'Must return some object')
        self.assertGreater(len(projectDictionary), 0, 'Hopefully some objects')

    def testGetProjectId(self):

        adapter: TodoistAdapter = self._adapter

        projectDictionary: ProjectDictionary = adapter._getCurrentProjects()

        projectId: int = adapter._getProjectId(projectName=ProjectName('Bogus'), projectDictionary=projectDictionary)

        self.assertNotEqual(0, projectId,  'I expected some id')

    def testGetExistingProjectId(self):

        adapter: TodoistAdapter = self._adapter

        projectDictionary: ProjectDictionary = adapter._getCurrentProjects()

        actualId: int = adapter._getProjectId(projectName=ProjectName('Personal'), projectDictionary=projectDictionary)

        project: Project = projectDictionary['Personal']
        expectedId: int = project['id']

        self.assertEqual(expectedId, actualId, 'I was supposed to get an actual ID')

    def testGetProjectTasks(self):

        adapter: TodoistAdapter = self._adapter

        projectDictionary: ProjectDictionary = adapter._getCurrentProjects()

        projectId: int = adapter._getProjectId(projectName=ProjectName('MockProject'), projectDictionary=projectDictionary)

        mileStoneTasks, devTasks = adapter._getProjectTasks(projectId=projectId)

        self.assertIsNotNone(mileStoneTasks, 'I need some test milestone tasks')
        self.assertIsNotNone(devTasks, 'I need some test developer tasks')

        self.assertEqual(NUMBER_OF_TEST_MILESTONE_TASKS, len(mileStoneTasks), 'I gotta have some mock milestone tasks')
        self.assertEqual(NUMBER_OF_TEST_DEV_TASKS,       len(devTasks),       'I gotta have some mock dev tasks')


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestTodoistAdapterReal))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
