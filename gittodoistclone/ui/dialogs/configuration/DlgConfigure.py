
from wx import BK_DEFAULT
from wx import BOTH
from wx import CANCEL
from wx import DEFAULT_DIALOG_STYLE
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

from gittodoistclone.ui.dialogs.configuration.GitHubConfigurationPanel import GitHubConfigurationPanel
from gittodoistclone.ui.dialogs.configuration.TodoistConfigurationPanel import TodoistConfigurationPanel
from gittodoistclone.ui.dialogs.configuration.TokensConfigurationPanel import TokensConfigurationPanel


class DlgConfigure(SizedDialog):

    def __init__(self, parent: Window, wxID: int = wxNewIdRef()):

        super().__init__(parent, wxID, 'Configure', style=DEFAULT_DIALOG_STYLE)

        # self._preferences: Preferences = Preferences()

        self.Center(BOTH)
        pane: SizedPanel = self.GetContentsPane()

        pane.SetSizerType('vertical')

        book: Notebook = Notebook(pane, ID_ANY, style=BK_DEFAULT | NB_TOP)

        tokensConfigurationPanel:  TokensConfigurationPanel  = TokensConfigurationPanel(book)
        todoistConfigurationPanel: TodoistConfigurationPanel = TodoistConfigurationPanel(book)
        gitHubConfigurationPanel:  GitHubConfigurationPanel = GitHubConfigurationPanel(book)

        book.AddPage(tokensConfigurationPanel,  'Tokens',  select=False)
        book.AddPage(todoistConfigurationPanel, 'Todoist', select=False)
        book.AddPage(gitHubConfigurationPanel,  'GitHub',  select=True)

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
