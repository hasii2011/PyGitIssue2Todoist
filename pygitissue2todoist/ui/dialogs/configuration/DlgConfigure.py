
from wx import BK_DEFAULT
from wx import BOTH
from wx import CANCEL
from wx import CAPTION
from wx import CLOSE_BOX

from wx import DIALOG_EX_METAL
from wx import EVT_BUTTON
from wx import EVT_CLOSE
from wx import ID_ANY
from wx import ID_CANCEL
from wx import ID_OK
from wx import NB_TOP
from wx import OK

from wx import Notebook
from wx import CommandEvent
from wx import Window

from wx import NewIdRef as wxNewIdRef

from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel

from pygitissue2todoist.ui.dialogs.configuration.GitHubConfigurationPanel import GitHubConfigurationPanel
from pygitissue2todoist.ui.dialogs.configuration.TodoistConfigurationPanel import TodoistConfigurationPanel
from pygitissue2todoist.ui.dialogs.configuration.TokensConfigurationPanel import TokensConfigurationPanel


class DlgConfigure(SizedDialog):

    def __init__(self, parent: Window, wxID: int = wxNewIdRef()):
        """

        Args:
            parent:   Parent window
            wxID:   A control ID if caller wants one
        """

        super().__init__(parent, wxID, 'Configure', style=CAPTION | CLOSE_BOX | DIALOG_EX_METAL)

        self.Center(BOTH)
        pane: SizedPanel = self.GetContentsPane()

        pane.SetSizerType('vertical')

        book: Notebook = Notebook(pane, ID_ANY, style=BK_DEFAULT | NB_TOP)

        tokensConfigurationPanel:  TokensConfigurationPanel  = TokensConfigurationPanel(book)
        todoistConfigurationPanel: TodoistConfigurationPanel = TodoistConfigurationPanel(book)
        gitHubConfigurationPanel:  GitHubConfigurationPanel = GitHubConfigurationPanel(book)

        book.AddPage(tokensConfigurationPanel,  'Tokens',  select=True)
        book.AddPage(todoistConfigurationPanel, 'Todoist', select=False)
        book.AddPage(gitHubConfigurationPanel,  'GitHub',  select=False)

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(OK | CANCEL))

        self.Fit()
        self.SetMinSize(self.GetSize())

        self.Bind(EVT_BUTTON, self.__onCmdOk, id=ID_OK)
        self.Bind(EVT_BUTTON, self.__onClose, id=ID_CANCEL)
        self.Bind(EVT_CLOSE,  self.__onClose)

    def __onCmdOk(self, event: CommandEvent):
        """
        If Skip(true) is called, the event processing system continues searching for a further handler
        function for this event,  even though it has been processed already in the current handler.
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
