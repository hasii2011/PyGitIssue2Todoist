
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from pygitissue2todoist.adapters.TodoistAdapter import GitIssueInfo

from tests.TestBase import TestBase


class TestTodoistAdapterBase(TestBase):
    """
    Base class for the todoist adapter unit tests.  Capture common code here
    """

    EXPECTED_NUMBER_OF_CALLBACKS: int = 6

    baseClsLogger: Logger = cast(Logger, None)

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestTodoistAdapterBase.baseClsLogger = getLogger(__name__)

    def setUp(self):
        self._cbInvoked:     bool = False
        self._cbInvokeCount: int = 0

    def _sampleCallback(self, statusMsg: str):

        TestTodoistAdapterBase.baseClsLogger.info(f'{statusMsg=}')

        self._cbInvoked     = True
        self._cbInvokeCount += 1

    def _createTasksToClone(self) -> List[GitIssueInfo]:
        taskList: List[GitIssueInfo] = []

        taskNames: List[str] = ['TaskOpie', 'TaskGabby10Meows', 'TaskFranny']

        for taskName in taskNames:
            taskInfo: GitIssueInfo = GitIssueInfo()

            taskInfo.gitIssueName = taskName
            taskInfo.gitIssueURL  = f'https://{taskName}.org'

            taskList.append(taskInfo)

        return taskList
