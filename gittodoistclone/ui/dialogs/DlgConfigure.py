
from typing import Tuple

from wx import ALIGN_CENTER_VERTICAL
from wx import ALIGN_LEFT
from wx import ALL
from wx import BOTH
from wx import CANCEL
from wx import EVT_BUTTON
from wx import EVT_CLOSE
from wx import EXPAND
from wx import HORIZONTAL
from wx import ICON_ERROR
from wx import ID_ANY
from wx import ID_CANCEL
from wx import ID_OK
from wx import OK
from wx import TOP
from wx import VERTICAL

from wx import StaticText
from wx import TextCtrl
from wx import CommandEvent
from wx import DefaultPosition
from wx import DefaultSize
from wx import Dialog
from wx import BoxSizer
from wx import StdDialogButtonSizer
from wx import StaticBox
from wx import StaticBoxSizer
from wx import Window

from wx import NewIdRef as wxNewIdRef

from wx.lib.agw.genericmessagedialog import GenericMessageDialog


from gittodoistclone.general.Preferences import Preferences

FrameWidth  = 400       # Canvas width
FrameHeight = 300       # and height


class DlgConfigure(Dialog):

    def __init__(self, parent: Window, wxID: int = wxNewIdRef()):

        super().__init__(parent, wxID, 'Configure', DefaultPosition, DefaultSize)

        self.Center(BOTH)

        box:       StaticBox      = StaticBox(self, ID_ANY, "")
        mainSizer: StaticBoxSizer = StaticBoxSizer(box, VERTICAL)

        border: BoxSizer = BoxSizer()
        border.Add(mainSizer, 1, EXPAND | ALL, 3)

        inp: BoxSizer             = self.__createTokenContainers()
        hs:  StdDialogButtonSizer  = self._createDialogButtonsContainer()
        mainSizer.Add(inp, 1, EXPAND | ALL)
        mainSizer.Add(hs, 1, EXPAND | ALL)

        self.SetAutoLayout(True)
        self.SetSizer(border)

        border.Fit(self)
        border.SetSizeHints(self)

        self.Bind(EVT_BUTTON, self.__onCmdOk, id=ID_OK)
        self.Bind(EVT_BUTTON, self.__onClose, id=ID_CANCEL)

        self.Bind(EVT_CLOSE,  self.__onClose)

        self._preferences: Preferences = Preferences()

    @property
    def todoistToken(self) -> str:
        return self._txtTodoistToken.GetValue()

    @property
    def githubToken(self) -> str:
        return self._txtGithubToken.GetValue()

    def _createDialogButtonsContainer(self, buttons=OK | CANCEL) -> StdDialogButtonSizer:

        hs: StdDialogButtonSizer = self.CreateSeparatedButtonSizer(buttons)
        return hs

    def __createTokenContainers(self) -> BoxSizer:

        szrTodoist,    txtTodoistToken = self.__createTextInputContainer('Todoist Token:')
        szrGithub,     txtGithubToken  = self.__createTextInputContainer('Github Token:')
        szrGithubName, txtGithubName   = self. __createTextInputContainer('Github User Name:')

        self._txtTodoistToken: TextCtrl = txtTodoistToken
        self._txtGithubToken:  TextCtrl = txtGithubToken
        self._txtGithubName:   TextCtrl = txtGithubName

        mainTokensContainer: BoxSizer = BoxSizer(VERTICAL)

        mainTokensContainer.Add(szrTodoist,    1, ALIGN_LEFT | TOP, 5)
        mainTokensContainer.Add(szrGithub,     1, ALIGN_LEFT | TOP, 9)
        mainTokensContainer.Add(szrGithubName, 1, ALIGN_LEFT | TOP, 2)

        return mainTokensContainer

    def __createTextInputContainer(self, label: str) -> Tuple[BoxSizer, TextCtrl]:

        boxSizer: BoxSizer = BoxSizer(HORIZONTAL)

        label:   StaticText = StaticText(self, ID_ANY, label)
        txtCtrl: TextCtrl   = TextCtrl(self, ID_ANY, "", size=(175, -1))

        boxSizer.Add(label,   1, ALIGN_CENTER_VERTICAL)
        boxSizer.Add(txtCtrl, 1, ALIGN_CENTER_VERTICAL)

        boxSizer.Fit(self)
        return boxSizer, txtCtrl

    def __onCmdOk(self, event: CommandEvent):
        """
        If Skip(true) is called, the event processing system continues searching for a further handler
        function for this event,  even though it has been processed already in the current handler.
        """
        self._preferences.todoistApiToken = self._txtTodoistToken.GetValue()
        self._preferences.githubApiToken  = self._txtGithubToken.GetValue()
        self._preferences.githubUserName  = self._txtGithubName.GetValue()

        if self.__areAllValueSupplied() is True:
            event.Skip(skip=True)
            self.SetReturnCode(OK)
            self.EndModal(OK)
        else:
            event.Skip(skip=False)
            dlg = GenericMessageDialog(self, 'You must supply all configuration parameters', "", agwStyle=ICON_ERROR | OK)
            dlg.ShowModal()
            dlg.Destroy()

    # noinspection PyUnusedLocal
    def __onClose(self, event: CommandEvent):
        """
        """
        self.SetReturnCode(CANCEL)
        self.EndModal(CANCEL)

    def __areAllValueSupplied(self) -> bool:

        ans: bool = True
        preferences: Preferences = self._preferences

        todoistApiToken: str = preferences.todoistApiToken
        githubApiToken:  str = preferences.githubApiToken
        githubUserName:  str = preferences.githubUserName

        if len(todoistApiToken) == 0 or len(githubApiToken) or len(githubUserName):
            ans = False

        return ans
