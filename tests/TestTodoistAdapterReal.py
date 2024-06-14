

from unittest import TestSuite
from unittest import main as unitTestMain

from todoist_api_python.models import Comment
from todoist_api_python.models import Project
from todoist_api_python.models import Task

from pygitissue2todoist.adapters.TodoistAdapter import ProjectDictionary
from pygitissue2todoist.adapters.TodoistAdapter import ProjectName
from pygitissue2todoist.adapters.TodoistAdapter import ProjectTasks
from pygitissue2todoist.adapters.TodoistAdapter import GitIssueInfo
from pygitissue2todoist.adapters.TodoistAdapter import TodoistAdapter
from pygitissue2todoist.adapters.TodoistAdapter import CloneInformation
from pygitissue2todoist.general.GitHubURLOption import GitHubURLOption

from pygitissue2todoist.general.Preferences import Preferences
from pygitissue2todoist.general.exceptions.NoteCreationError import NoteCreationError

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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Preferences.determinePreferencesLocation()

    def setUp(self):

        super().setUp()
        preferences: Preferences = Preferences()
        self._adapter: TodoistAdapter = TodoistAdapter(apiToken=preferences.todoistApiToken)

    def tearDown(self):
        super().tearDown()

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

        projectId: str = adapter._getProjectId(projectName=ProjectName('Bogus'), projectDictionary=projectDictionary)

        self.assertNotEqual(0, projectId,  'I expected some id')

    def testGetExistingProjectId(self):

        adapter: TodoistAdapter = self._adapter

        projectDictionary: ProjectDictionary = adapter._getCurrentProjects()

        actualId: str = adapter._getProjectId(projectName=ProjectName('Personal'), projectDictionary=projectDictionary)

        project: Project = projectDictionary[ProjectName('Personal')]
        expectedId: str = project.id

        self.assertEqual(expectedId, actualId, 'I was supposed to get an actual ID')

    def testGetProjectTaskItems(self):

        adapter: TodoistAdapter = self._adapter

        projectDictionary: ProjectDictionary = adapter._getCurrentProjects()

        projectId: str = adapter._getProjectId(projectName=ProjectName('MockProject'), projectDictionary=projectDictionary)

        projectTasks: ProjectTasks = adapter._getProjectTaskItems(projectId=projectId)

        self.assertIsNotNone(projectTasks.mileStoneTasks, 'I need some test milestone tasks')
        self.assertIsNotNone(projectTasks.devTasks, 'I need some test developer tasks')

        self.assertEqual(NUMBER_OF_TEST_MILESTONE_TASKS, len(projectTasks.mileStoneTasks), 'I gotta have some mock milestone tasks')
        self.assertEqual(NUMBER_OF_TEST_DEV_TASKS,       len(projectTasks.devTasks),       'I gotta have some mock dev tasks')

    def testGetProjectTaskItemsForNewProject(self):

        adapter: TodoistAdapter = self._adapter

        projectId: str = self._getAProjectId(projectName=ProjectName('NewProject'))
        projectTasks: ProjectTasks = adapter._getProjectTaskItems(projectId=projectId)

        self.assertIsNotNone(projectTasks, 'I a basic data class return')
        self.assertIsNotNone(projectTasks.mileStoneTasks, 'I need some test milestone tasks')
        self.assertIsNotNone(projectTasks.devTasks, 'I need some test developer tasks')

        self.assertEqual(0, len(projectTasks.mileStoneTasks), 'New Projects have no milestone tasks')
        self.assertEqual(0, len(projectTasks.devTasks),       'New Projects have no dev tasks')

    def testGetMilestoneTaskItemExisting(self):

        adapter: TodoistAdapter = self._adapter

        projectId: str = self._getAProjectId(projectName=ProjectName('MockProject'))

        info: CloneInformation = CloneInformation()
        info.repositoryTask    = 'MockProject'
        info.milestoneNameTask = 'MockMilestone2'
        info.tasksToClone      = [GitIssueInfo(gitIssueName='MockTask3'), GitIssueInfo(gitIssueName='MockTask4')]

        milestoneTask: Task = adapter._getMilestoneTaskItem(projectId=projectId, milestoneName='MockMilestone2', progressCb=self._sampleCallback)

        taskName: str = milestoneTask.content
        self.assertEqual('MockMilestone2', taskName, 'Should get existing item')

    def testAddNoteToSubTask(self):
        adapter: TodoistAdapter = self._adapter

        projectDictionary: ProjectDictionary = adapter._getCurrentProjects()

        projectId: str = adapter._getProjectId(projectName=ProjectName('MockProject'), projectDictionary=projectDictionary)

        projectTasks: ProjectTasks = adapter._getProjectTaskItems(projectId=projectId)

        devTasks = projectTasks.devTasks
        for devTask in devTasks:
            taskName: str = devTask.content
            taskId:   str = devTask.id
            self.logger.info(f'{taskName} - {taskId=}')

            try:
                noteToAdd: str = f'https://{taskName}-{taskId}.com'

                comment: Comment = adapter._addNoteToTask(itemId=taskId, noteContent=noteToAdd)
                self.logger.info(f'Comment added: {comment}')
            except NoteCreationError as nce:
                self.logger.error(f'{nce.errorCode=} {nce.message=}')

    def testAddTaskAsHyperlink(self):
        # markdown Link format
        # [here](https://github.com/hasii2011/gittodoistclone/wiki/How-to-use-gittodoistclone)

        hyperLinkedTask: GitIssueInfo = GitIssueInfo()
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

    def _getAProjectId(self, projectName: ProjectName) -> str:

        adapter: TodoistAdapter = self._adapter

        projectDictionary: ProjectDictionary = adapter._getCurrentProjects()

        projectId: str = adapter._getProjectId(projectName=projectName, projectDictionary=projectDictionary)

        return projectId


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestTodoistAdapterReal))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
