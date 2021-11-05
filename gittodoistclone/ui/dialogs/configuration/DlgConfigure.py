
from typing import List
from typing import cast

from wx import BK_DEFAULT
from wx import BOTH
from wx import CANCEL
from wx import DEFAULT_DIALOG_STYLE
from wx import EVT_BUTTON
from wx import EVT_CHECKBOX
from wx import EVT_CLOSE
from wx import EVT_RADIOBOX
from wx import ICON_ERROR
from wx import ID_ANY
from wx import ID_CANCEL
from wx import ID_OK

from wx import NB_TOP
from wx import NOT_FOUND
from wx import Notebook
from wx import OK
from wx import RA_SPECIFY_COLS

from wx import DefaultPosition
from wx import DefaultSize

from wx import RadioBox
from wx import StaticText
from wx import TextCtrl
from wx import CheckBox
from wx import CommandEvent
from wx import Window

from wx import NewIdRef as wxNewIdRef

from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel

from wx.lib.agw.genericmessagedialog import GenericMessageDialog

from gittodoistclone.general.GitHubURLOption import GitHubURLOption
from gittodoistclone.general.Preferences import Preferences
from gittodoistclone.ui.dialogs.configuration.TodoistConfigurationPanel import TodoistConfigurationPanel
from gittodoistclone.ui.dialogs.configuration.TokensConfigurationPanel import TokensConfigurationPanel


class DlgConfigure(SizedDialog):

    def __init__(self, parent: Window, wxID: int = wxNewIdRef()):

        super().__init__(parent, wxID, 'Configure', style=DEFAULT_DIALOG_STYLE)

        self._preferences: Preferences = Preferences()

        self._txtTodoistToken:    TextCtrl = cast(TextCtrl, None)
        self._txtGithubToken:     TextCtrl = cast(TextCtrl, None)
        self._txtGithubName:      TextCtrl = cast(TextCtrl, None)
        self._cacheOptionControl: CheckBox = cast(CheckBox, None)
        self._radioBoxURLOption:  RadioBox = cast(RadioBox, None)

        self.Center(BOTH)
        pane: SizedPanel = self.GetContentsPane()

        pane.SetSizerType('vertical')

        book: Notebook = Notebook(pane, ID_ANY, style=BK_DEFAULT | NB_TOP)

        tokensConfigurationPanel:  TokensConfigurationPanel  = TokensConfigurationPanel(book)
        todoistConfigurationPanel: TodoistConfigurationPanel = TodoistConfigurationPanel(book)

        book.AddPage(tokensConfigurationPanel,  'Tokens',  select=False)
        book.AddPage(todoistConfigurationPanel, 'Todoist', select=True)

        # self._createGitHubURLOptionControl(pane)
        # self._createCacheOptionControl(pane)
        # self._setPreferencesValues()

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(OK | CANCEL))

        self.Fit()
        self.SetMinSize(self.GetSize())

        self.Bind(EVT_BUTTON, self.__onCmdOk, id=ID_OK)
        self.Bind(EVT_BUTTON, self.__onClose, id=ID_CANCEL)

        self.Bind(EVT_RADIOBOX, self.__onGitHubURLOptionChanged, self._radioBoxURLOption)
        self.Bind(EVT_CHECKBOX, self.__OnCacheOption, self._cacheOptionControl)
        self.Bind(EVT_CLOSE,  self.__onClose)

    # noinspection SpellCheckingInspection
    @property
    def todoistToken(self) -> str:
        return self._txtTodoistToken.GetValue()

    @property
    def githubToken(self) -> str:
        return self._txtGithubToken.GetValue()

    def _createTokenControls(self, sizedPanel: SizedPanel):

        txtTodoistToken = self.__createTextInputControls('Todoist Token:', sizedPanel)
        txtGithubToken  = self.__createTextInputControls('Github Token:', sizedPanel)
        txtGithubName   = self.__createTextInputControls('Github User Name:', sizedPanel)

        self._txtTodoistToken = txtTodoistToken
        self._txtGithubToken  = txtGithubToken
        self._txtGithubName  = txtGithubName

    def _createCacheOptionControl(self, sizedPanel: SizedPanel):

        checkBoxPanel: SizedPanel = SizedPanel(sizedPanel, ID_ANY)
        checkBoxPanel.SetSizerType('horizontal')
        # noinspection PyUnresolvedReferences
        checkBoxPanel.SetSizerProps(expand=True)

        self._cacheOptionControl = CheckBox(parent=checkBoxPanel, label="Allow Todoist Cache Cleanup", id=ID_ANY)

    def _createGitHubURLOptionControl(self, sizedPanel: SizedPanel):

        options: List[str] = [GitHubURLOption.DoNotAdd.value, GitHubURLOption.AddAsDescription. value,
                              GitHubURLOption.AddAsComment.value, GitHubURLOption.HyperLinkedTaskName.value
                              ]
        self._radioBoxURLOption = RadioBox(parent=sizedPanel, id=ID_ANY,
                                           label="Include GitHub Issue URL", pos=DefaultPosition, size=DefaultSize,
                                           choices=options, majorDimension=1, style=RA_SPECIFY_COLS
                                           )

    def _setPreferencesValues(self):

        preferences: Preferences = self._preferences

        # self._txtTodoistToken.SetValue(preferences.todoistApiToken)
        # self._txtGithubToken.SetValue(preferences.githubApiToken)
        # self._txtGithubName.SetValue(preferences.githubUserName)

        idx: int = self._radioBoxURLOption.FindString(preferences.githubURLOption.value, bCase=False)
        assert idx != NOT_FOUND, "Developer Error; Enumeration may have changed"
        self._radioBoxURLOption.SetSelection(idx)

        if preferences.cleanTodoistCache is True:
            self._cacheOptionControl.SetValue(True)
        else:
            self._cacheOptionControl.SetValue(False)

    def __createTextInputControls(self, label: str, sizedPanel: SizedPanel) -> TextCtrl:

        # noinspection PyUnusedLocal
        sText:   StaticText = StaticText(sizedPanel, ID_ANY, label)
        txtCtrl: TextCtrl   = TextCtrl(sizedPanel, ID_ANY, "", size=(315, -1))
        return txtCtrl

    def __onCmdOk(self, event: CommandEvent):
        """
        If Skip(true) is called, the event processing system continues searching for a further handler
        function for this event,  even though it has been processed already in the current handler.
        """
        # self._preferences.todoistApiToken = self._txtTodoistToken.GetValue()
        # self._preferences.githubApiToken  = self._txtGithubToken.GetValue()
        # self._preferences.githubUserName  = self._txtGithubName.GetValue()

        if self.__areAllValuesSupplied() is True:
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

    def __onGitHubURLOptionChanged(self, event: CommandEvent):

        selectedIdx: int = event.GetInt()
        print(f'__onGitHubURLOptionChanged - {selectedIdx}')

        selectedOption: str             = self._radioBoxURLOption.GetString(selectedIdx)
        newOption:      GitHubURLOption = GitHubURLOption(selectedOption)

        self._preferences.githubURLOption = newOption

    def __OnCacheOption(self, event: CommandEvent):
        if event.IsChecked() is True:
            self._preferences.cleanTodoistCache = True
        else:
            self._preferences.cleanTodoistCache = False

    def __areAllValuesSupplied(self) -> bool:

        ans: bool = True
        preferences: Preferences = self._preferences

        todoistApiToken: str = preferences.todoistApiToken
        githubApiToken:  str = preferences.githubApiToken
        githubUserName:  str = preferences.githubUserName

        if len(todoistApiToken) == 0 or len(githubApiToken) == 0 or len(githubUserName) == 0:
            ans = False

        return ans
