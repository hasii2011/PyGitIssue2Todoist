
from typing import cast

from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from todoist.models import Item
from todoist.models import Note
from todoist.models import Project

from gittodoistclone.adapters.TodoistAdapter import ProjectDictionary
from gittodoistclone.adapters.TodoistAdapter import ProjectName
from gittodoistclone.adapters.TodoistAdapter import ProjectTasks
from gittodoistclone.adapters.TodoistAdapter import TaskInfo
from gittodoistclone.adapters.TodoistAdapter import TodoistAdapter
from gittodoistclone.adapters.TodoistAdapter import CloneInformation
from gittodoistclone.general.GitHubURLOption import GitHubURLOption

from gittodoistclone.general.Preferences import Preferences
from gittodoistclone.general.exceptions.NoteCreationError import NoteCreationError

from tests.TestTodoistAdapterBase import TestTodoistAdapterBase

NUMBER_OF_TEST_MILESTONE_TASKS: int = 2
NUMBER_OF_TEST_DEV_TASKS:       int = 4


class TestTodoistAdapterReal(TestTodoistAdapterBase):
    """
    This unit test uses real credentials to test the todoist adapter.

    For the tests against the MockProject make sure your account has a project with
    the following name and structure

    ```
        MockProject
            MockMileStone1
                MockTask1
                MockTask2
            MockMileStone2
                MockTask3
                MockTask4
    ```
    """
    clsLogger: Logger = cast(Logger, None)

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
        ci.tasksToClone      = self._createTasksToClone()

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

    def testGetProjectTaskItems(self):

        adapter: TodoistAdapter = self._adapter

        projectDictionary: ProjectDictionary = adapter._getCurrentProjects()

        projectId: int = adapter._getProjectId(projectName=ProjectName('MockProject'), projectDictionary=projectDictionary)

        projectTasks: ProjectTasks = adapter._getProjectTaskItems(projectId=projectId)

        self.assertIsNotNone(projectTasks.mileStoneTasks, 'I need some test milestone tasks')
        self.assertIsNotNone(projectTasks.devTasks, 'I need some test developer tasks')

        self.assertEqual(NUMBER_OF_TEST_MILESTONE_TASKS, len(projectTasks.mileStoneTasks), 'I gotta have some mock milestone tasks')
        self.assertEqual(NUMBER_OF_TEST_DEV_TASKS,       len(projectTasks.devTasks),       'I gotta have some mock dev tasks')

    def testGetProjectTaskItemsForNewProject(self):

        adapter: TodoistAdapter = self._adapter

        # projectDictionary: ProjectDictionary = adapter._getCurrentProjects()

        # projectId: int = adapter._getProjectId(projectName=ProjectName('NewProject'), projectDictionary=projectDictionary)
        projectId: int = self._getAProjectId(projectName=ProjectName('NewProject'))
        projectTasks: ProjectTasks = adapter._getProjectTaskItems(projectId=projectId)

        self.assertIsNotNone(projectTasks, 'I a basic data class return')
        self.assertIsNotNone(projectTasks.mileStoneTasks, 'I need some test milestone tasks')
        self.assertIsNotNone(projectTasks.devTasks, 'I need some test developer tasks')

        self.assertEqual(0, len(projectTasks.mileStoneTasks), 'New Projects have no milestone tasks')
        self.assertEqual(0, len(projectTasks.devTasks),       'New Projects have no dev tasks')

    def testGetMilestoneTaskItemExisting(self):

        adapter: TodoistAdapter = self._adapter

        projectId: int = self._getAProjectId(projectName=ProjectName('MockProject'))

        info: CloneInformation = CloneInformation()
        info.repositoryTask    = 'MockProject'
        info.milestoneNameTask = 'MockMilestone2'
        info.tasksToClone      = ['MockTask3', 'MockTask4']

        milestoneTaskItem: Item = adapter._getMilestoneTaskItem(projectId=projectId, milestoneNameTask='MockMilestone2', progressCb=self._sampleCallback)

        itemName: str = milestoneTaskItem['content']
        self.assertEqual('MockMilestone2', itemName, 'Should get existing item')

    def testAddNoteToSubTask(self):
        adapter: TodoistAdapter = self._adapter

        projectDictionary: ProjectDictionary = adapter._getCurrentProjects()

        projectId: int = adapter._getProjectId(projectName=ProjectName('MockProject'), projectDictionary=projectDictionary)

        projectTasks: ProjectTasks = adapter._getProjectTaskItems(projectId=projectId)

        devTasks = projectTasks.devTasks
        for devTask in devTasks:
            taskName: str = devTask["content"]
            taskId:   int = devTask["id"]
            self.logger.info(f'{taskName} - {taskId=}')

            try:
                noteToAdd: str = f'https://{taskName}-{taskId}.com'

                note: Note = adapter.addNoteToTask(itemId=taskId, noteContent=noteToAdd)
                self.logger.info(f'Note added: {note}')
            except NoteCreationError as nce:
                self.logger.error(f'{nce.errorCode=} {nce.message=}')

    def testAddTaskAsHyperlink(self):
        # markdown Link format
        # [here](https://github.com/hasii2011/gittodoistclone/wiki/How-to-use-gittodoistclone)

        hyperLinkedTask: TaskInfo = TaskInfo()
        hyperLinkedTask.gitIssueName = f'I am linked'
        hyperLinkedTask.gitIssueURL  = 'https://hsanchezii.wordpress.com'

        ci: CloneInformation = CloneInformation()
        ci.repositoryTask    = 'MockUser/MockRepo'
        ci.milestoneNameTask = 'MockMilestone'
        ci.tasksToClone      = [hyperLinkedTask]

        preferences: Preferences = Preferences()

        savedOption: GitHubURLOption = preferences.githubURLOption
        preferences.githubURLOption  = GitHubURLOption.HyperLinkedTaskName
        
        adapter: TodoistAdapter = self._adapter
        adapter.createTasks(ci, self._sampleCallback)

        preferences.githubURLOption = savedOption

    def _getAProjectId(self, projectName: ProjectName) -> int:

        adapter: TodoistAdapter = self._adapter

        projectDictionary: ProjectDictionary = adapter._getCurrentProjects()

        projectId: int = adapter._getProjectId(projectName=projectName, projectDictionary=projectDictionary)

        return projectId


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestTodoistAdapterReal))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
