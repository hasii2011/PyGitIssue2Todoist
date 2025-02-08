
from typing import List, cast

from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import PropertyMock

from todoist_api_python.models import Project

from pygitissue2todoist.adapters.TodoistAdapter import ProjectData
from pygitissue2todoist.adapters.TodoistAdapter import TodoistAdapter
from pygitissue2todoist.adapters.TodoistAdapter import CloneInformation

# from pygitissue2todoist.adapters.TodoistAdapterAssigned import TodoistAdapterAssigned
from pygitissue2todoist.adapters.TodoistAdapterTypes import GitIssueInfo
from pygitissue2todoist.general.PreferencesV2 import PreferencesV2
from tests.TestTodoistAdapterBase import TestTodoistAdapterBase
from pygitissue2todoist.adapters.ModeAdapter import Mode

class TestTodoistAdapterAssignment(TestTodoistAdapterBase):
    """
    This unit test uses mocks to test the todoist adapter.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()




    def setUp(self):
        super().setUp()

        preferences: PreferencesV2 = PreferencesV2()
        preferences.mode = Mode.SingleProjectAssigneeMode
        self._adapter: TodoistAdapter = TodoistAdapter(apiToken=preferences.todoistAPIToken)


    def tearDown(self):
        super().tearDown()

    def testMultipleRepos(self):
        print('testMultipleRepos')

        dummy_tasks: List[GitIssueInfo] = []

        clone_info: CloneInformation = CloneInformation(
            repositoryTask= 'dummy_repo_task',
            milestoneNameTask = 'dummy_milestone_task',
            tasksToClone = dummy_tasks,
        )

        self._adapter.createTasks(clone_info, lambda x: print(x))

        self.fail('Not implemented')



def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestTodoistAdapterAssignment))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
