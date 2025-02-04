
from typing import List

from pygitissue2todoist.adapters.TodoistAdapter import GitIssueInfo

from tests.ProjectTestBase import ProjectTestBase


class TestTodoistAdapterBase(ProjectTestBase):
    """
    Base class for the todoist adapter unit tests.  Capture common code here
    """

    EXPECTED_NUMBER_OF_CALLBACKS: int = 6

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self._cbInvoked:     bool = False
        self._cbInvokeCount: int = 0

    def _sampleCallback(self, statusMsg: str):

        self.logger.info(f'{statusMsg=}')

        self._cbInvoked     = True
        self._cbInvokeCount += 1

    def _createTasksToClone(self) -> List[GitIssueInfo]:
        taskList: List[GitIssueInfo] = []

        taskNames: List[str] = ['TaskOpie', 'TaskGabby10Meows', 'TaskFranny']

        for idx, taskName in enumerate(taskNames):
            taskInfo: GitIssueInfo = GitIssueInfo()

            taskInfo.gitIssueName = taskName
            taskInfo.gitIssueURL  = f'https://github.com/octocat/Hello-World/issues/{idx}'

            taskList.append(taskInfo)

        return taskList
