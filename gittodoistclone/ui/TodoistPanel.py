
from typing import List
from typing import cast

from dataclasses import dataclass
from dataclasses import field

from logging import Logger
from logging import getLogger

from todoist import TodoistAPI
from todoist.models import Item
from todoist.models import Project

from wx import ALIGN_RIGHT
from wx import ALL
from wx import BU_LEFT
from wx import EVT_BUTTON
from wx import EXPAND
from wx import HORIZONTAL
from wx import LB_ALWAYS_SB
from wx import LB_OWNERDRAW
from wx import PD_ELAPSED_TIME
from wx import VERTICAL

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

from gittodoistclone.general.Preferences import Preferences
from gittodoistclone.ui.BasePanel import BasePanel


@dataclass
class CloneInformation:
    repositoryTask:    str = ''
    milestoneNameTask: str = ''
    tasksToClone:      List[str] = field(default_factory=list)


class TodoistPanel(BasePanel):

    def __init__(self, parent: Window):

        super().__init__(parent)

        self.SetBackgroundColour(self.backgroundColor)

        self.logger: Logger = getLogger(__name__)

        contentSizer: BoxSizer = self._layoutContent()

        self.SetSizer(contentSizer)
        self.Fit()

        self._cloneInformation: CloneInformation = cast(CloneInformation, None)

        self._apiToken: str        = Preferences().todoistApiToken
        self._todoist:  TodoistAPI = TodoistAPI(self._apiToken)

    @property
    def tasksToClone(self) -> CloneInformation:
        return self._cloneInformation

    @tasksToClone.setter
    def tasksToClone(self, newInfo: CloneInformation):

        self._cloneInformation = newInfo
        self._taskList.SetItems(newInfo.tasksToClone)
        self._createTaskButton.Enable(True)

    def _layoutContent(self) -> BoxSizer:

        sizer: BoxSizer       = BoxSizer(VERTICAL)
        tz:    StaticBoxSizer = self._createTodoTaskList()
        bz:    BoxSizer       = self._createTasksButton()

        sizer.Add(tz, BasePanel.PROPORTION_CHANGEABLE,     ALL | EXPAND, 1)
        sizer.Add(bz, BasePanel.PROPORTION_NOT_CHANGEABLE, ALL | ALIGN_RIGHT, 2)

        return sizer

    def _createTodoTaskList(self) -> StaticBoxSizer:

        taskWxID: int = wxNewIdRef()

        self._taskList: ListBox = ListBox(self, taskWxID, style=LB_OWNERDRAW | LB_ALWAYS_SB)
        self._taskList.Enable(False)

        sz = StaticBoxSizer(VERTICAL, self, "Todoist Tasks")
        sz.Add(self._taskList, BasePanel.PROPORTION_CHANGEABLE, EXPAND)

        self._taskList.SetItems(['Empty'])
        return sz

    def _createTasksButton(self) -> BoxSizer:

        bSizer:         BoxSizer = BoxSizer(HORIZONTAL)
        createTaskWxID: int      = wxNewIdRef()

        self._createTaskButton: Button = Button(self, id=createTaskWxID, style=BU_LEFT, label='Create Tasks')

        self._createTaskButton.Enable(False)
        bSizer.Add(self._createTaskButton, BasePanel.PROPORTION_NOT_CHANGEABLE, ALL, 1)

        self.Bind(EVT_BUTTON, self._onCreateTaskClicked, id=createTaskWxID)
        return bSizer

    # noinspection PyUnusedLocal
    def _onCreateTaskClicked(self, event: CommandEvent):

        dlg: ProgressDialog = self.__setupProgressDialog()

        self.__updateDialog('Start', 750)
        todoist: TodoistAPI       = self._todoist
        ci:      CloneInformation = self._cloneInformation

        justRepoName: str     = ci.repositoryTask.split('/')[1]
        project:      Project = todoist.projects.add(justRepoName)
        self.__updateDialog(f'Added {justRepoName}', 750)

        milestoneTaskItem: Item = todoist.items.add(ci.milestoneNameTask, project_id=project['id'])

        self.__updateDialog(f'Added Milestone: {ci.milestoneNameTask}')

        tasks: List[str] = ci.tasksToClone
        #
        # To create subtasks first create in project then move them to the milestone task
        #
        for task in tasks:
            subTask: Item = todoist.items.add(task, project_id=project['id'])
            subTask.move(parent_id=milestoneTaskItem['id'])

        self.__updateDialog('Start Sync', 750)
        self._todoist.sync()
        self.__updateDialog('Committing', 750)
        self._todoist.commit()

        self.__updateDialog('Done', 1000)
        dlg.Destroy()

    def __setupProgressDialog(self) -> ProgressDialog:

        self._progressDlg: ProgressDialog = ProgressDialog("Creating Tasks", "An informative message", parent=self, style=PD_ELAPSED_TIME)

        return self._progressDlg

    def __updateDialog(self, newMsg: str, delay: int = 500):

        self._progressDlg.Pulse(newMsg)
        wxYield()
        wxMilliSleep(delay)
