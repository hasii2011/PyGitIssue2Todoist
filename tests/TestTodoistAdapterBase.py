
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from gittodoistclone.adapters.TodoistAdapter import TaskInfo

from tests.TestBase import TestBase


class TestTodoistAdapterBase(TestBase):
    """
    Base class for the todoist adapter unit tests.  Capture common code here
    """

    EXPECTED_NUMBER_OF_CALLBACKS: int = 7

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

    def _createTasksToClone(self) -> List[TaskInfo]:
        taskList: List[TaskInfo] = []

        taskNames: List[str] = ['TaskOpie', 'TaskGabby10Meows', 'TaskFranny']

        for taskName in taskNames:
            taskInfo: TaskInfo = TaskInfo()

            taskInfo.gitIssueName = taskName
            taskInfo.gitIssueURL  = f'https://{taskName}.org'

            taskList.append(taskInfo)

        return taskList
