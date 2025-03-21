
from typing import cast

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

from tests.TodoistStrategyUnitTestBase import TodoistStrategyUnitTestBase


class TestTodoistAdapterMock(TodoistStrategyUnitTestBase):
    """
    This unit test uses mocks to test the todoist adapter.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def testMockedApi(self):
        pass
        # ci: CloneInformation = CloneInformation()
        # ci.repositoryTask    = 'MockUser/MockRepo'
        # ci.milestoneNameTask = 'MockMilestone'
        # ci.tasksToClone      = self._createTasksToClone()
        #
        # adapter: TodoistAdapter = TodoistAdapter(apiToken='mockApiToken')
        #
        # adapter._todoist = Mock()
        #
        # mockProject: MagicMock = MagicMock(spec=Project)   # So I can get subscription
        # mockProject.id      = 'DEADBEEF'
        # mockProject.content = 'MockProject'
        #
        # mockState = MagicMock()
        # mockState['projects'].return_value = [mockProject]
        #
        # projectDataItems: ProjectData = ProjectData({'items': []})
        #
        # type(adapter._todoist).state    = PropertyMock(mockState)
        #
        # adapter._todoist.projects.add.return_value = mockProject
        #
        # mockItem: MagicMock    = MagicMock()
        # mockItem['id']         = 'MockItemId'
        #
        # adapter._todoist.items.add.return_value = mockItem
        #
        # mockedSyncResponse: MagicMock = MagicMock()
        # mockedSyncResponse['sync_token'] = 'MockedSyncToken-DEADBEEF'
        # mockedSyncResponse['items']      = ''
        # mockedSyncResponse['notes']      = ''
        #
        # adapter._todoist.sync.return_value = mockedSyncResponse
        # #
        # # crap load of mocking is done
        # #
        # adapter.createTasks(info=ci, progressCb=self._sampleCallback)
        #
        # self.assertTrue(self._cbInvoked, 'Looks like callback was never invoked')
        # self.assertEqual(TodoistStrategyUnitTestBase.EXPECTED_NUMBER_OF_CALLBACKS, self._cbInvokeCount, 'Callback invoked an incorrect number of times')
        #


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestTodoistAdapterMock))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
