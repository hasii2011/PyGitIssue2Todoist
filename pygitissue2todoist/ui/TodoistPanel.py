
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from wx import EVT_BUTTON

from wx import ICON_ERROR
from wx import ID_ANY
from wx import LB_ALWAYS_SB
from wx import LB_OWNERDRAW
from wx import OK
from wx import PD_ELAPSED_TIME

from wx import MessageDialog
from wx import Button
from wx import ProgressDialog
from wx import CommandEvent
from wx import ListBox

from wx import Yield as wxYield
from wx import MilliSleep as wxMilliSleep

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

from wx.lib.agw.genericmessagedialog import GenericMessageDialog

from pygitissue2todoist.ErrorHandler import ErrorHandler

# from pygitissue2todoist.adapters.AbstractTodoistAdapter import AbstractTodoistAdapter
from pygitissue2todoist.adapters.AdapterAuthenticationError import AdapterAuthenticationError

from pygitissue2todoist.strategy.TodoistStrategyTypes import CloneInformation
from pygitissue2todoist.strategy.TodoistStrategyTypes import GitIssueInfo
# from pygitissue2todoist.strategy.StrategyTypes import TodoistAdapter

# from pygitissue2todoist.adapters.TodoistAdapterSingleProject import TodoistAdapterSingleProject

from pygitissue2todoist.general.Preferences import Preferences

from pygitissue2todoist.general.exceptions.NoteCreationError import NoteCreationError
from pygitissue2todoist.general.exceptions.TaskCreationError import TaskCreationError

from pygitissue2todoist.strategy.TodoistCreation import TodoistCreation

from pygitissue2todoist.ui.dialogs.configuration.DlgConfigure import DlgConfigure
from pygitissue2todoist.ui.eventengine.Events import EVT_MILESTONE_SELECTED
from pygitissue2todoist.ui.eventengine.Events import MilestoneSelectedEvent
from pygitissue2todoist.ui.eventengine.IEventEngine import IEventEngine

from pygitissue2todoist.ui.BasePanel import BasePanel
from pygitissue2todoist.ui.eventengine.Events import EventType


class TodoistPanel(BasePanel):

    def __init__(self, parent: SizedPanel, eventEngine: IEventEngine):

        super().__init__(parent)

        self.SetSizerType('vertical')
        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True, proportion=1)

        self.SetBackgroundColour(self.backgroundColor)

        self.logger: Logger = getLogger(__name__)

        self._eventEngine:      IEventEngine     = eventEngine
        self._cloneInformation: CloneInformation = cast(CloneInformation, None)

        self._preferences: Preferences = Preferences()
        self._apiToken:    str         = self._preferences.todoistAPIToken

        # if self._preferences.singleTodoistProject is True:
        #     self._todoistAdapter: AbstractTodoistAdapter = TodoistAdapterSingleProject(apiToken=self._apiToken)
        # else:
        #     self._todoistAdapter = TodoistAdapter(self._apiToken)
        self._todoistCreation: TodoistCreation = TodoistCreation()

        self._taskList:         ListBox = cast(ListBox, None)
        self._createTaskButton: Button  = cast(Button, None)

        self._layoutContent(parent=self)

        self.Bind(EVT_BUTTON, self._onCreateTaskClicked, self._createTaskButton)

        self._eventEngine.registerListener(event=EVT_MILESTONE_SELECTED, callback=self._onMileStoneSelected)

    @property
    def tasksToClone(self) -> CloneInformation:
        return self._cloneInformation

    @tasksToClone.setter
    def tasksToClone(self, newInfo: CloneInformation):

        self._cloneInformation = newInfo
        tasksToClone: List[GitIssueInfo] = newInfo.tasksToClone
        for taskToClone in tasksToClone:
            self._taskList.Append(taskToClone.gitIssueName, taskToClone)

        # noinspection PyUnresolvedReferences
        self._createTaskButton.Enable(True)

    def clearTasks(self):
        self._taskList.Clear()

    # noinspection PyUnusedLocal
    def _onMileStoneSelected(self, event: MilestoneSelectedEvent):
        self.clearTasks()
        self._createTaskButton.Disable()

    def _layoutContent(self, parent: SizedPanel):

        self._layoutTodoTaskList(parent=parent)
        self._layoutTasksButton(parent=parent)

    def _layoutTodoTaskList(self, parent: SizedPanel):

        box: SizedStaticBox = SizedStaticBox(parent, ID_ANY, "Todoist Tasks")
        box.SetSizerProps(expand=True, proportion=4)

        self._taskList = ListBox(box, style=LB_OWNERDRAW | LB_ALWAYS_SB)
        self._taskList.SetSizerProps(expand=True, proportion=1)
        self._taskList.Enable(False)

        self._taskList.SetItems(['Empty'])

    def _layoutTasksButton(self, parent: SizedPanel):

        sizedPanel: SizedPanel = SizedPanel(parent)
        sizedPanel.SetSizerType('horizontal')
        sizedPanel.SetSizerProps(expand=False, halign='right')  # expand False allows aligning right

        self._createTaskButton = Button(sizedPanel, label='Create Tasks')
        self._createTaskButton.Disable()

    # noinspection PyUnusedLocal
    def _onCreateTaskClicked(self, event: CommandEvent):

        dlg: ProgressDialog = self._setupProgressDialog()

        ci: CloneInformation = self._cloneInformation

        # adapter: AbstractTodoistAdapter = self._todoistAdapter

        try:
            # adapter.createTasks(info=ci, progressCb=self._adapterCallback)
            self._todoistCreation.createTasks(info=ci, progressCb=self._adapterCallback)
            self._progressDlg.Destroy()
            self.clearTasks()
        except AdapterAuthenticationError as e:
            self._progressDlg.Destroy()
            self._handleAuthenticationError(event)
        except (TaskCreationError, NoteCreationError) as tce:
            self._progressDlg.Destroy()
            errorHandler: ErrorHandler = ErrorHandler()

            if errorHandler.isErrorHandled(tce.errorCode) is True:
                errorHandler.handleError(tce.message, tce.errorCode)
            else:
                booBoo: MessageDialog = MessageDialog(parent=None, message=tce.message, caption='Task Creation Error!', style=OK | ICON_ERROR)
                booBoo.ShowModal()
        except Exception as ue:
            message: str = str(ue)
            uhOh: MessageDialog = MessageDialog(parent=None, message=message, caption='Task Creation Error!', style=OK | ICON_ERROR)
            uhOh.ShowModal()
        finally:
            self._eventEngine.sendEvent(eventType=EventType.TaskCreationComplete)

    def _setupProgressDialog(self) -> ProgressDialog:

        self._progressDlg: ProgressDialog = ProgressDialog("Creating Tasks", "", style=PD_ELAPSED_TIME)

        return self._progressDlg

    def _adapterCallback(self, statusMsg: str):
        self._updateDialog(newMsg=statusMsg)

    def _updateDialog(self, newMsg: str, delay: int = 500):

        self._progressDlg.Pulse(newMsg)
        wxYield()
        wxMilliSleep(delay)

    def _handleAuthenticationError(self, event: CommandEvent):

        eDlg = GenericMessageDialog(self, 'The supplied todoist token is invalid', "", agwStyle=ICON_ERROR | OK)
        eDlg.ShowModal()
        eDlg.Destroy()
        with DlgConfigure(self) as aDlg:
            cDlg: DlgConfigure = cast(DlgConfigure, aDlg)
            if cDlg.ShowModal() == OK:
                # The following 2 already defined in init
                # self._apiToken       = Preferences().todoistAPIToken
                self._todoistCreation = TodoistCreation()

                self._onCreateTaskClicked(event)    # Dang I hate recursion
