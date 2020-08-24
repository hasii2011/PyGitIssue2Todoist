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
from wx import Sizer
from wx import StaticBox
from wx import StaticBoxSizer
from wx import Window

from wx import NewIdRef as wxNewIdRef


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

        inp: BoxSizer = self.__createTokenContainers(parentSizer=mainSizer)
        hs:  Sizer    = self._createDialogButtonsContainer()
        mainSizer.Add(inp, 1, EXPAND | ALL)
        mainSizer.Add(hs, 1, EXPAND | ALL)

        self.SetAutoLayout(True)
        self.SetSizer(border)

        border.Fit(self)
        border.SetSizeHints(self)

        self.Bind(EVT_BUTTON, self.__onCmdOk, id=ID_OK)
        self.Bind(EVT_BUTTON, self.__onClose, id=ID_CANCEL)

        self.Bind(EVT_CLOSE,  self.__onClose)

    @property
    def todoistToken(self) -> str:
        return self._txtTodoistToken.GetValue()

    @property
    def githubToken(self) -> str:
        return self._txtGithubToken.GetValue()

    def _createDialogButtonsContainer(self, buttons=OK | CANCEL) -> Sizer:

        hs: Sizer = self.CreateSeparatedButtonSizer(buttons)
        return hs

    def __createTokenContainers(self, parentSizer: Sizer) -> BoxSizer:

        szrTodoist, txtTodoistToken = self.__createTokenContainer('Todoist Token:')
        szrGithub,  txtGithubToken  = self.__createTokenContainer('Github Token:')

        self._txtTodoistToken: TextCtrl = txtTodoistToken
        self._txtGithubToken:  TextCtrl = txtGithubToken

        mainTokensContainer: BoxSizer = BoxSizer(VERTICAL)

        mainTokensContainer.Add(szrTodoist, 1, ALIGN_LEFT | TOP, 5)
        mainTokensContainer.Add(szrGithub,  1, ALIGN_LEFT | TOP, 5)

        return mainTokensContainer

    def __createTokenContainer(self, label: str) -> Tuple[BoxSizer, TextCtrl]:

        boxSizer: BoxSizer = BoxSizer(HORIZONTAL)

        label:   StaticText = StaticText(self, ID_ANY, label)
        txtCtrl: TextCtrl   = TextCtrl(self, ID_ANY, "", size=(175, -1))

        boxSizer.Add(label,   1, ALIGN_CENTER_VERTICAL)
        boxSizer.Add(txtCtrl, 1, ALIGN_CENTER_VERTICAL)

        boxSizer.Fit(self)
        return boxSizer, txtCtrl

    def __onCmdOk(self, event: CommandEvent):
        """
        """
        event.Skip(skip=True)
        self.SetReturnCode(OK)
        self.EndModal(OK)

    # noinspection PyUnusedLocal
    def __onClose(self, event: CommandEvent):
        """
        """
        self.SetReturnCode(CANCEL)
        self.EndModal(CANCEL)
