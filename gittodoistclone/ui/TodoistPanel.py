
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ALIGN_RIGHT
from wx import ALL
from wx import BU_LEFT
from wx import EVT_BUTTON
from wx import EXPAND
from wx import HORIZONTAL
from wx import ICON_ERROR
from wx import LB_ALWAYS_SB
from wx import LB_OWNERDRAW
from wx import OK
from wx import PD_ELAPSED_TIME
from wx import VERTICAL

from wx import MessageDialog
from wx import Button
from wx import ProgressDialog
from wx import CommandEvent
from wx import ListBox
from wx import StaticBoxSizer
from wx import BoxSizer
from wx import Window

from wx import NewIdRef as wxNewIdRef
from wx import Yield as wxYield
from wx import MilliSleep as wxMilliSleep

from wx.lib.agw.genericmessagedialog import GenericMessageDialog

from gittodoistclone.ErrorHandler import ErrorHandler
from gittodoistclone.adapters.AbstractTodoistAdapter import AbstractTodoistAdapter

from gittodoistclone.adapters.AdapterAuthenticationError import AdapterAuthenticationError
from gittodoistclone.adapters.TodoistAdapter import CloneInformation
from gittodoistclone.adapters.TodoistAdapter import TaskInfo
from gittodoistclone.adapters.TodoistAdapter import TodoistAdapter
from gittodoistclone.adapters.TodoistAdapterSingleProject import TodoistAdapterSingleProject

from gittodoistclone.general.Preferences import Preferences
from gittodoistclone.general.exceptions.NoteCreationError import NoteCreationError
from gittodoistclone.general.exceptions.TaskCreationError import TaskCreationError

from gittodoistclone.ui.BasePanel import BasePanel
from gittodoistclone.ui.dialogs.configuration.DlgConfigure import DlgConfigure


class TodoistPanel(BasePanel):

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.SetBackgroundColour(self.backgroundColor)

        self.logger: Logger = getLogger(__name__)

        contentSizer: BoxSizer = self._layoutContent()

        # noinspection PyUnresolvedReferences
        self.SetSizer(contentSizer)
        self.Fit()

        self._cloneInformation: CloneInformation = cast(CloneInformation, None)

        self._preferences: Preferences = Preferences()
        self._apiToken:        str            = self._preferences.todoistApiToken
        if self._preferences.tasksInParentProject is True:
            self._todoistAdapter: AbstractTodoistAdapter = TodoistAdapterSingleProject(apiToken=self._apiToken)
        else:
            self._todoistAdapter = TodoistAdapter(self._apiToken)

    @property
    def tasksToClone(self) -> CloneInformation:
        return self._cloneInformation

    @tasksToClone.setter
    def tasksToClone(self, newInfo: CloneInformation):

        self._cloneInformation = newInfo
        tasksToClone: List[TaskInfo] = newInfo.tasksToClone
        for taskToClone in tasksToClone:
            self._taskList.Append(taskToClone.gitIssueName, taskToClone)

        # noinspection PyUnresolvedReferences
        self._createTaskButton.Enable(True)

    def _layoutContent(self) -> BoxSizer:

        sizer: BoxSizer       = BoxSizer(VERTICAL)
        tz:    StaticBoxSizer = self._createTodoTaskList()
        bz:    BoxSizer       = self._createTasksButton()

        sizer.Add(tz, BasePanel.PROPORTION_CHANGEABLE,     ALL | EXPAND, 1)
        sizer.Add(bz, BasePanel.PROPORTION_NOT_CHANGEABLE, ALL | ALIGN_RIGHT, 2)

        return sizer

    def clearTasks(self):
        self._taskList.Clear()

    def _createTodoTaskList(self) -> StaticBoxSizer:

        taskWxID: int = wxNewIdRef()

        self._taskList: ListBox = ListBox(self, taskWxID, style=LB_OWNERDRAW | LB_ALWAYS_SB)
        # noinspection PyUnresolvedReferences
        self._taskList.Enable(False)

        sz = StaticBoxSizer(VERTICAL, self, "Todoist Tasks")
        sz.Add(self._taskList, BasePanel.PROPORTION_CHANGEABLE, EXPAND)

        self._taskList.SetItems(['Empty'])
        return sz

    def _createTasksButton(self) -> BoxSizer:

        bSizer:         BoxSizer = BoxSizer(HORIZONTAL)
        createTaskWxID: int      = wxNewIdRef()

        self._createTaskButton: Button = Button(self, id=createTaskWxID, style=BU_LEFT, label='Create Tasks')

        # noinspection PyUnresolvedReferences
        self._createTaskButton.Disable()
        bSizer.Add(self._createTaskButton, BasePanel.PROPORTION_NOT_CHANGEABLE, ALL, 1)

        self.Bind(EVT_BUTTON, self._onCreateTaskClicked, id=createTaskWxID)
        return bSizer

    # noinspection PyUnusedLocal
    def _onCreateTaskClicked(self, event: CommandEvent):

        dlg: ProgressDialog = self.__setupProgressDialog()

        ci: CloneInformation = self._cloneInformation

        adapter: AbstractTodoistAdapter = self._todoistAdapter

        try:
            adapter.createTasks(info=ci, progressCb=self.__adapterCallback)
            self._progressDlg.Destroy()
        except AdapterAuthenticationError as e:
            self._progressDlg.Destroy()
            self.__handleAuthenticationError(event)
        except (TaskCreationError, NoteCreationError) as tce:
            self._progressDlg.Destroy()
            errorHandler: ErrorHandler = ErrorHandler()

            if errorHandler.isErrorHandled(tce.errorCode) is True:
                errorHandler.handleError(tce.message, tce.errorCode)
            else:
                booBoo: MessageDialog = MessageDialog(parent=None, message=tce.message, caption='Task Creation Error!', style=OK | ICON_ERROR)
                booBoo.ShowModal()

    def __setupProgressDialog(self) -> ProgressDialog:

        self._progressDlg: ProgressDialog = ProgressDialog("Creating Tasks", "", parent=self, style=PD_ELAPSED_TIME)

        return self._progressDlg

    def __adapterCallback(self, statusMsg: str):
        self.__updateDialog(newMsg=statusMsg)

    def __updateDialog(self, newMsg: str, delay: int = 500):

        self._progressDlg.Pulse(newMsg)
        wxYield()
        wxMilliSleep(delay)

    def __handleAuthenticationError(self, event: CommandEvent):

        eDlg = GenericMessageDialog(self, 'The supplied todoist token is invalid', "", agwStyle=ICON_ERROR | OK)
        eDlg.ShowModal()
        eDlg.Destroy()
        with DlgConfigure(self) as aDlg:
            cDlg: DlgConfigure = cast(DlgConfigure, aDlg)
            if cDlg.ShowModal() == OK:
                # The following 2 already defined in init
                self._apiToken       = Preferences().todoistApiToken
                self._todoistAdapter = TodoistAdapter(self._apiToken)

                self._onCreateTaskClicked(event)    # Dang I hate recursion
