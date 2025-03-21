
from unittest import TestSuite
from unittest import main as unitTestMain

from todoist_api_python.models import Comment
from todoist_api_python.models import Project
from todoist_api_python.models import Task

from pygitissue2todoist.general.GitHubURLOption import GitHubURLOption

from pygitissue2todoist.general.Preferences import Preferences

from pygitissue2todoist.general.exceptions.NoteCreationError import NoteCreationError

from pygitissue2todoist.strategy.AbstractTodoistStrategy import ProjectDictionary
from pygitissue2todoist.strategy.AbstractTodoistStrategy import ProjectName

from pygitissue2todoist.strategy.StrategyTypes import CloneInformation
from pygitissue2todoist.strategy.StrategyTypes import GitIssueInfo

from pygitissue2todoist.strategy.TodoistCreateByRepository import ProjectTasks
from pygitissue2todoist.strategy.TodoistCreateByRepository import TodoistCreateByRepository


from tests.TodoistStrategyUnitTestBase import TodoistStrategyUnitTestBase

MOCK_PROJECT_NAME: str = 'MockProject'

NUMBER_OF_TEST_MILESTONE_TASKS: int = 2
NUMBER_OF_TEST_DEV_TASKS:       int = 4


class TestTodoistCreateByRepository(TodoistStrategyUnitTestBase):
    """
    This unit test uses real credentials to test the todoist single project strategy.

    For the tests against the MockProject make sure your account has a project with
    the following name and structure

    ```
        MockProject
            MockMilestone1
                MockTask1
                MockTask2
            MockMilestone2
                MockTask3
                MockTask4
    ```
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):

        super().setUp()

        self._strategy: TodoistCreateByRepository = TodoistCreateByRepository()

    def tearDown(self):
        super().tearDown()

    def testRealAPI(self):

        ci: CloneInformation = CloneInformation()
        ci.repositoryTask    = 'MockUser/MockRepo'
        ci.milestoneNameTask = 'MockMilestone'
        ci.tasksToClone      = self._createTasksToClone()

        self._strategy.createTasks(info=ci, progressCb=self._sampleCallback)

    def testGetCurrentProjects(self):

        strategy: TodoistCreateByRepository = self._strategy

        projectDictionary: ProjectDictionary = strategy._getCurrentProjects()

        self.assertIsNotNone(projectDictionary, 'Must return some object')
        self.assertGreater(len(projectDictionary), 0, 'Hopefully some objects')

    def testGetProjectId(self):

        strategy: TodoistCreateByRepository = self._strategy

        projectDictionary: ProjectDictionary = strategy._getCurrentProjects()

        projectId: str = strategy._getProjectId(projectName=ProjectName('Bogus'), projectDictionary=projectDictionary)

        self.assertNotEqual(0, projectId,  'I expected some id')

    def testGetExistingProjectId(self):

        strategy: TodoistCreateByRepository = self._strategy

        projectDictionary: ProjectDictionary = strategy._getCurrentProjects()

        actualId: str = strategy._getProjectId(projectName=ProjectName('Personal'), projectDictionary=projectDictionary)

        project: Project = projectDictionary[ProjectName('Personal')]
        expectedId: str = project.id

        self.assertEqual(expectedId, actualId, 'I was supposed to get an actual ID')

    def testGetProjectTaskItems(self):

        strategy: TodoistCreateByRepository = self._strategy

        projectDictionary: ProjectDictionary = strategy._getCurrentProjects()

        projectId: str = strategy._getProjectId(projectName=ProjectName(MOCK_PROJECT_NAME), projectDictionary=projectDictionary)

        projectTasks: ProjectTasks = strategy._getProjectTaskItems(projectId=projectId)

        self.assertIsNotNone(projectTasks.mileStoneTasks, 'I need some test milestone tasks')
        self.assertIsNotNone(projectTasks.devTasks, 'I need some test developer tasks')

        self.assertEqual(NUMBER_OF_TEST_MILESTONE_TASKS, len(projectTasks.mileStoneTasks), 'I gotta have some mock milestone tasks')
        self.assertEqual(NUMBER_OF_TEST_DEV_TASKS,       len(projectTasks.devTasks),       'I gotta have some mock dev tasks')

    def testGetProjectTaskItemsForNewProject(self):

        strategy: TodoistCreateByRepository = self._strategy

        projectId: str = self._getAProjectId(projectName=ProjectName('NewProject'))
        projectTasks: ProjectTasks = strategy._getProjectTaskItems(projectId=projectId)

        self.assertIsNotNone(projectTasks, 'I a basic data class return')
        self.assertIsNotNone(projectTasks.mileStoneTasks, 'I need some test milestone tasks')
        self.assertIsNotNone(projectTasks.devTasks, 'I need some test developer tasks')

        self.assertEqual(0, len(projectTasks.mileStoneTasks), 'New Projects have no milestone tasks')
        self.assertEqual(0, len(projectTasks.devTasks),       'New Projects have no dev tasks')

    def testGetMilestoneTaskItemExisting(self):

        strategy: TodoistCreateByRepository = self._strategy

        projectId: str = self._getAProjectId(projectName=ProjectName(MOCK_PROJECT_NAME))

        info: CloneInformation = CloneInformation()
        info.repositoryTask    = MOCK_PROJECT_NAME
        info.milestoneNameTask = 'MockMilestone2'
        info.tasksToClone      = [GitIssueInfo(gitIssueName='MockTask3'), GitIssueInfo(gitIssueName='MockTask4')]

        milestoneTask: Task = strategy._getMilestoneTaskItem(projectId=projectId, milestoneName='MockMilestone2', progressCb=self._sampleCallback)

        taskName: str = milestoneTask.content
        self.assertEqual('MockMilestone2', taskName, 'Should get existing item')

    def testAddNoteToSubTask(self):

        strategy: TodoistCreateByRepository = self._strategy

        projectDictionary: ProjectDictionary = strategy._getCurrentProjects()

        projectId: str = strategy._getProjectId(projectName=ProjectName(MOCK_PROJECT_NAME), projectDictionary=projectDictionary)

        projectTasks: ProjectTasks = strategy._getProjectTaskItems(projectId=projectId)

        devTasks = projectTasks.devTasks
        for devTask in devTasks:
            taskName: str = devTask.content
            taskId:   str = devTask.id
            self.logger.info(f'{taskName} - {taskId=}')

            try:
                noteToAdd: str = f'https://{taskName}-{taskId}.com'

                comment: Comment = strategy._addNoteToTask(itemId=taskId, noteContent=noteToAdd)
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

        savedOption: GitHubURLOption = preferences.gitHubURLOption
        preferences.gitHubURLOption  = GitHubURLOption.HyperLinkedTaskName

        strategy: TodoistCreateByRepository = self._strategy
        strategy.createTasks(ci, self._sampleCallback)

        preferences.gitHubURLOption = savedOption

    def _getAProjectId(self, projectName: ProjectName) -> str:

        strategy: TodoistCreateByRepository = self._strategy

        projectDictionary: ProjectDictionary = strategy._getCurrentProjects()

        projectId: str = strategy._getProjectId(projectName=projectName, projectDictionary=projectDictionary)

        return projectId


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()

    testSuite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestTodoistCreateByRepository))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
