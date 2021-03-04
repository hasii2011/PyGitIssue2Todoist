
from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import PropertyMock

from todoist.managers.items import ItemsManager
from todoist.managers.projects import ProjectsManager
from todoist.models import Project

from gittodoistclone.adapters.TodoistAdapter import TodoistAdapter
from gittodoistclone.adapters.TodoistAdapter import CloneInformation

from tests.TestTodoistAdapterBase import TestTodoistAdapterBase


class TestTodoistAdapterMock(TestTodoistAdapterBase):
    """
    This unit test uses mocks to test the todoist adapter.
    """
    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestTodoistAdapterBase.setUpClass()
        TestTodoistAdapterMock.clsLogger = getLogger(__name__)

    def setUp(self):
        self.logger: Logger = TestTodoistAdapterMock.clsLogger
        super().setUp()

    def tearDown(self):
        pass

    def testMockedApi(self):

        ci: CloneInformation = CloneInformation()
        ci.repositoryTask    = 'MockUser/MockRepo'
        ci.milestoneNameTask = 'MockMilestone'
        ci.tasksToClone      = ['TaskOpie', 'TaskGabby10Meows', 'TaskFranny']

        adapter: TodoistAdapter = TodoistAdapter(apiToken='mockApiToken')

        adapter._todoist = Mock()
        projectsManager  = Mock(spec=ProjectsManager)
        itemsManager     = Mock(spec=ItemsManager)

        mockProject: MagicMock = MagicMock(spec=Project)   # So I can get subscription
        mockProject['id']      = 'DEADBEEF'
        mockProject['name']    = 'MockProject'

        mockState = MagicMock()
        mockState['projects'].return_value = [mockProject]

        adapter._todoist.projects.return_value = projectsManager
        adapter._todoist.items.return_value    = itemsManager
        type(adapter._todoist).state    = PropertyMock(mockState)

        adapter._todoist.projects.add.return_value = mockProject

        mockItem: MagicMock    = MagicMock()
        mockItem['id']         = 'MockItemId'

        adapter._todoist.items.add.return_value = mockItem

        mockedSyncResponse: MagicMock = MagicMock()
        mockedSyncResponse['sync_token'] = 'MockedSyncToken-DEADBEEF'
        mockedSyncResponse['items']      = ''
        mockedSyncResponse['notes']      = ''

        adapter._todoist.sync.return_value = mockedSyncResponse
        #
        # crap load of mocking is done
        #
        adapter.createTasks(info=ci, progressCb=self._sampleCallback)

        self.assertTrue(self._cbInvoked, 'Looks like callback was never invoked')
        self.assertEqual(TestTodoistAdapterMock.EXPECTED_NUMBER_OF_CALLBACKS, self._cbInvokeCount, 'Callback invoked an incorrect number of times')


def suite() -> TestSuite:
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestTodoistAdapterMock))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
