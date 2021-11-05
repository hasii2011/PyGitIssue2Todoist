
from typing import cast

from wx import Notebook

from gittodoistclone.ui.dialogs.configuration.PreferencesPanel import PreferencesPanel
from gittodoistclone.ui.dialogs.configuration.TextContainer import TextContainer


class TokensConfigurationPanel(PreferencesPanel):

    def __init__(self, parent: Notebook):

        self._txtTodoistContainer:      TextContainer = cast(TextContainer, None)
        self._txtGitHubTokenContainer:  TextContainer = cast(TextContainer, None)
        self._txtGitHubNameContainer:   TextContainer = cast(TextContainer, None)

        super().__init__(parent)

        self.SetSizerType('vertical')

    def _createControls(self):
        """
        Implement parent empty method
        Creates the panel's control containers and stash them as private instance variables
        """
        self._txtTodoistContainer     = TextContainer(parent=self, labelText='Todoist Token:',    valueChangedCallback=self.__onTodoistTokenChange)
        self._txtGitHubTokenContainer = TextContainer(parent=self, labelText='GitHub Token:',     valueChangedCallback=self.__onGitHubTokenChange)
        self._txtGitHubNameContainer  = TextContainer(parent=self, labelText='GitHub User Name:', valueChangedCallback=self.__onGitHubUserNameChange)

    def _setControlValues(self):
        """
        Implement parent empty method
        Set the default values on the controls.
        """
        self._txtTodoistContainer.textValue     = self._preferences.todoistApiToken
        self._txtGitHubNameContainer.textValue  = self._preferences.githubUserName
        self._txtGitHubTokenContainer.textValue = self._preferences.githubApiToken

    def __onTodoistTokenChange(self, newValue: str):

        self._preferences.todoistApiToken = newValue

    def __onGitHubTokenChange(self, newValue: str):
        self._preferences.githubApiToken = newValue

    def __onGitHubUserNameChange(self, newValue: str):
        self._preferences.githubUserName = newValue
