
from typing import cast

from wx import CommandEvent
from wx import EVT_CHECKBOX
from wx import ID_ANY

from wx import CheckBox
from wx import Notebook

from wx import NewIdRef as wxNewIdRef


from pygitissue2todoist.ui.dialogs.configuration.AbstractConfigurationPanel import AbstractConfigurationPanel
from pygitissue2todoist.ui.dialogs.configuration.TextContainer import TextContainer


class TodoistConfigurationPanel(AbstractConfigurationPanel):

    def __init__(self, parent: Notebook):

        self._cacheOptionControl:         CheckBox      = cast(CheckBox, None)
        self._tasksInParentOption:        CheckBox      = cast(CheckBox, None)
        self._parentProjectNameContainer: TextContainer = cast(TextContainer, None)

        super().__init__(parent)

        self.SetSizerType('vertical')

        self._textId: int = cast(int, None)

        self.Bind(EVT_CHECKBOX, self.__onCacheOption,          self._cacheOptionControl)
        self.Bind(EVT_CHECKBOX, self.__onTasksInParentProject, self._tasksInParentOption)

    def _createControls(self):
        """
        Creates the panel's controls and stashes them as private instance variables
        """
        self._textId = wxNewIdRef()

        self._cacheOptionControl         = CheckBox(parent=self, label="Allow Todoist Cache Cleanup", id=ID_ANY)
        self._tasksInParentOption        = CheckBox(parent=self, label="Single Todoist Project",     id=ID_ANY)
        self._parentProjectNameContainer = TextContainer(parent=self, labelText='Todoist Project Name:',
                                                         valueChangedCallback=self.__onParentProjectNameChange)

    def _setControlValues(self):
        """
        Set the current configuration values on the controls.
        """
        chkBoxValue: bool = self._preferences.singleTodoistProject
        self._tasksInParentOption.SetValue(chkBoxValue)

        self._parentProjectNameContainer.textValue = self._preferences.todoistProjectName

        if chkBoxValue is False:
            self._parentProjectNameContainer.textControlEnabled(False)

        if self._preferences.cleanTodoistCache is True:
            self._cacheOptionControl.SetValue(True)
        else:
            self._cacheOptionControl.SetValue(False)

    def __onParentProjectNameChange(self, newValue: str):
        self._preferences.todoistProjectName = newValue

    def __onTasksInParentProject(self, event: CommandEvent):

        if event.IsChecked() is True:
            self._preferences.singleTodoistProject = True
            self._parentProjectNameContainer.textControlEnabled(True)
        else:
            self._preferences.singleTodoistProject = False
            self._parentProjectNameContainer.textControlEnabled(False)

    def __onCacheOption(self, event: CommandEvent):
        if event.IsChecked() is True:
            self._preferences.cleanTodoistCache = True
        else:
            self._preferences.cleanTodoistCache = False
