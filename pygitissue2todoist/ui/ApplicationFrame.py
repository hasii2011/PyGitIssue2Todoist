
from typing import List
from typing import Tuple

from logging import Logger
from logging import getLogger

from wx import BOTH
from wx import DEFAULT_FRAME_STYLE
from wx import EVT_CLOSE
from wx import EVT_MENU
from wx import FRAME_EX_METAL
from wx import ID_PREFERENCES
from wx import OK
from wx import ID_ABOUT
from wx import ID_EXIT

from wx import Size
from wx import CommandEvent
from wx import Menu
from wx import MenuBar
from wx import StatusBar
from wx import Window

from wx import NewIdRef as wxNewIdRef
from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from pygitissue2todoist.adapters.GitHubAdapter import AbbreviatedGitIssues
from pygitissue2todoist.adapters.TodoistAdapter import GitIssueInfo

from pygitissue2todoist.general.Preferences import Preferences

from pygitissue2todoist.ui.GitHubPanel import GitHubPanel
from pygitissue2todoist.ui.TodoistPanel import CloneInformation
from pygitissue2todoist.ui.TodoistPanel import TodoistPanel
from pygitissue2todoist.ui.dialogs.DlgAbout import DlgAbout

from pygitissue2todoist.ui.dialogs.configuration.DlgConfigure import DlgConfigure
from pygitissue2todoist.ui.dialogs.DlgHelp import DlgHelp

from pygitissue2todoist.ui.eventengine.Events import EVT_ISSUES_SELECTED
from pygitissue2todoist.ui.eventengine.Events import EVT_REPOSITORY_SELECTED
from pygitissue2todoist.ui.eventengine.Events import IssuesSelectedEvent
from pygitissue2todoist.ui.eventengine.Events import RepositorySelectedEvent

from pygitissue2todoist.ui.eventengine.IEventEngine import IEventEngine
from pygitissue2todoist.ui.eventengine.EventEngine import EventEngine

class ApplicationFrame(SizedFrame):

    HELP_MENU_ID: int = wxNewIdRef()

    def __init__(self, parent: Window, wxID: int, title: str):

        self._preferences: Preferences = Preferences()
        appSize: Size = Size(self._preferences.startupWidth, self._preferences.startupHeight)

        super().__init__(parent=parent, id=wxID, title=title, size=appSize, style=DEFAULT_FRAME_STYLE | FRAME_EX_METAL)
        self.GetContentsPane().SetSizerType('horizontal')
        self.GetContentsPane().SetSizerProps(expand=True, proportion=1)
        self.logger: Logger = getLogger(__name__)

        self._eventEngine: IEventEngine = EventEngine(listeningWindow=self)

        self._status: StatusBar = self.CreateStatusBar()
        self._status.SetStatusText('Ready!')

        self._createApplicationMenuBar()
        self._githubPanel, self._todoistPanel = self._layoutApplicationContentArea()

        # self.SetThemeEnabled(True)

        x, y = self._preferences.appStartupPosition

        if x == str(Preferences.NO_DEFAULT_X) or y == str(Preferences.NO_DEFAULT_Y):
            self.Center(BOTH)  # Center on the screen
        else:
            appPosition: Tuple[int, int] = self._preferences.appStartupPosition
            self.SetPosition(pt=appPosition)

        self.Bind(EVT_CLOSE, self.Close)

        self._eventEngine.registerListener(event=EVT_REPOSITORY_SELECTED, callback=self._onRepositorySelected)
        self._eventEngine.registerListener(event=EVT_ISSUES_SELECTED,     callback=self._onIssuesSelected)

        # a little trick to make sure that you can't resize the dialog to
        # less screen space than the controls need
        # self.Fit()
        # self.SetMinSize(self.GetSize())

    # noinspection PyUnusedLocal
    def Close(self, force=False):

        ourSize: Tuple[int, int] = self.GetSize()
        self._preferences.startupWidth  = ourSize[0]
        self._preferences.startupHeight = ourSize[1]

        pos: Tuple[int, int] = self.GetPosition()
        self._preferences.appStartupPosition = pos

        self.Destroy()

    def _createApplicationMenuBar(self):

        menuBar:  MenuBar = MenuBar()
        fileMenu: Menu = Menu()
        helpMenu: Menu = Menu()

        fileMenu.Append(ID_PREFERENCES, 'Configure', 'Configure Application IDs')
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_EXIT, '&Quit', "Quit Application")

        helpMenu.Append(ApplicationFrame.HELP_MENU_ID, "&MiniHelp", "Simple Help")
        helpMenu.AppendSeparator()
        helpMenu.Append(ID_ABOUT, '&About', 'Tell you about me')

        menuBar.Append(fileMenu, 'File')
        menuBar.Append(helpMenu, 'Help')

        self.SetMenuBar(menuBar)

        self.Bind(EVT_MENU, self._onMiniHelp,  id=ApplicationFrame.HELP_MENU_ID)
        self.Bind(EVT_MENU, self._onConfigure, id=ID_PREFERENCES)
        self.Bind(EVT_MENU, self._onAbout,     id=ID_ABOUT)
        self.Bind(EVT_MENU, self.Close,        id=ID_EXIT)

    def _layoutApplicationContentArea(self) -> Tuple[GitHubPanel, TodoistPanel]:

        sizedPanel: SizedPanel = self.GetContentsPane()
        leftPanel:  GitHubPanel  = GitHubPanel(sizedPanel,  eventEngine=self._eventEngine)
        rightPanel: TodoistPanel = TodoistPanel(sizedPanel, eventEngine=self._eventEngine)


        # noinspection PyUnresolvedReferences
        # self.SetSizer(mainSizer)
        # mainSizer.Fit(self)       # Don't do this or setting of frame size won't work

        return leftPanel, rightPanel

    # noinspection PyUnusedLocal
    def _onRepositorySelected(self, event: RepositorySelectedEvent):

        self.logger.info(f'Clear the github issues list and todoist panel selection lists')

        self._githubPanel.clearIssues()
        self._todoistPanel.clearTasks()

    def _onIssuesSelected(self, event: IssuesSelectedEvent):

        adapterTaskInfo: List[GitIssueInfo] = self.__convertToTasksToClone(event.selectedSimpleGitIssues)
        cloneInformation: CloneInformation = CloneInformation()

        cloneInformation.repositoryTask    = event.repositoryName
        cloneInformation.milestoneNameTask = event.milestoneName
        cloneInformation.tasksToClone      = adapterTaskInfo

        self.logger.debug(f'{event.selectedSimpleGitIssues=}')

        self._todoistPanel.tasksToClone = cloneInformation

    # noinspection PyUnusedLocal
    def _onMiniHelp(self, event: CommandEvent):

        dlg: DlgHelp = DlgHelp(self)
        dlg.ShowModal()

    # noinspection PyUnusedLocal
    def _onConfigure(self, event: CommandEvent):

        dlg: DlgConfigure = DlgConfigure(self)
        if dlg.ShowModal() == OK:
            preferences: Preferences = Preferences()
            todoistToken:   str = preferences.todoistApiToken
            githubToken:    str = preferences.githubApiToken
            gitHubUserName: str = preferences.githubUserName
            self.logger.debug(f'{todoistToken=} - {githubToken=} {gitHubUserName=}')

    # noinspection PyUnusedLocal
    def _onAbout(self, event: CommandEvent):

        dlg: DlgAbout = DlgAbout(parent=self)
        dlg.ShowModal()

    def __convertToTasksToClone(self, abbreviatedGitIssues: AbbreviatedGitIssues) -> List[GitIssueInfo]:
        adapterTaskInfo: List[GitIssueInfo] = []

        for simpleGitIssue in abbreviatedGitIssues:
            taskInfo: GitIssueInfo = GitIssueInfo()
            taskInfo.gitIssueName = simpleGitIssue.issueTitle
            taskInfo.gitIssueURL  = simpleGitIssue.issueHTMLURL
            adapterTaskInfo.append(taskInfo)

        return adapterTaskInfo
