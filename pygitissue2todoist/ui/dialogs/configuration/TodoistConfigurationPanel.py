
from typing import List
from typing import cast

from wx import CommandEvent
from wx import DefaultPosition
from wx import DefaultSize
from wx import EVT_CHECKBOX
from wx import EVT_RADIOBOX
from wx import ID_ANY

from wx import CheckBox
from wx import NOT_FOUND
from wx import Notebook

from wx import NewIdRef as wxNewIdRef
from wx import RA_SPECIFY_COLS
from wx import RadioBox

from pygitissue2todoist.strategy.TodoistTaskCreationStrategy import TodoistTaskCreationStrategy
from pygitissue2todoist.ui.dialogs.configuration.AbstractConfigurationPanel import AbstractConfigurationPanel
from pygitissue2todoist.ui.dialogs.configuration.TextContainer import TextContainer

TASK_CREATION_STRATEGY_OPTIONS: List[str] = [
    TodoistTaskCreationStrategy.SINGLE_TODOIST_PROJECT.value,
    TodoistTaskCreationStrategy.PROJECT_BY_REPOSITORY.value,
    TodoistTaskCreationStrategy.ALL_ISSUES_ASSIGNED_TO_USER.value,
]


class TodoistConfigurationPanel(AbstractConfigurationPanel):

    def __init__(self, parent: Notebook):

        self._cacheOptionControl:         CheckBox      = cast(CheckBox, None)
        # self._tasksInParentOption:        CheckBox      = cast(CheckBox, None)
        self._taskCreationStrategyOption: RadioBox      = cast(RadioBox, None)
        self._parentProjectNameContainer: TextContainer = cast(TextContainer, None)

        super().__init__(parent)

        self.SetSizerType('vertical')

        self._textId: int = cast(int, None)

        self.Bind(EVT_CHECKBOX, self.__onCacheOption,        self._cacheOptionControl)
        self.Bind(EVT_RADIOBOX, self.__onTaskStrategyChanges, self._taskCreationStrategyOption)
        # self.Bind(EVT_CHECKBOX, self.__onTasksInParentProject, self._tasksInParentOption)

    def _layoutContent(self):
        """
        Creates the panel's controls and stashes them as private instance variables
        """
        self._textId = wxNewIdRef()

        self._cacheOptionControl         = CheckBox(parent=self, label="Allow Todoist Cache Cleanup", id=ID_ANY)
        self._layoutStrategySelector()
        self._parentProjectNameContainer = TextContainer(parent=self, labelText='Todoist Project Name:',
                                                         valueChangedCallback=self.__onParentProjectNameChange)

    def _layoutStrategySelector(self):

        self._taskCreationStrategyOption = RadioBox(parent=self, id=ID_ANY,
                                                    label="Todoist Task Creation Strategy",
                                                    pos=DefaultPosition,
                                                    size=DefaultSize,
                                                    choices=TASK_CREATION_STRATEGY_OPTIONS,
                                                    majorDimension=1,
                                                    style=RA_SPECIFY_COLS
                                                    )

    def _setControlValues(self):
        """
        Set the current configuration values on the controls.
        """
        # chkBoxValue: bool = self._preferences.singleTodoistProject
        # self._tasksInParentOption.SetValue(chkBoxValue)

        idx: int = self._taskCreationStrategyOption.FindString(self._preferences.taskCreationStrategy.value, bCase=False)
        assert idx != NOT_FOUND, "Developer Error; Enumeration may have changed"
        self._taskCreationStrategyOption.SetSelection(idx)

        self._parentProjectNameContainer.textValue = self._preferences.todoistProjectName

        option: RadioBox = self._taskCreationStrategyOption
        if option.GetString(option.GetSelection()) == TodoistTaskCreationStrategy.PROJECT_BY_REPOSITORY.value:
            self._parentProjectNameContainer.textControlEnabled(False)

        if self._preferences.cleanTodoistCache is True:
            self._cacheOptionControl.SetValue(True)
        else:
            self._cacheOptionControl.SetValue(False)

    def __onParentProjectNameChange(self, newValue: str):
        self._preferences.todoistProjectName = newValue

    def __onCacheOption(self, event: CommandEvent):
        if event.IsChecked() is True:
            self._preferences.cleanTodoistCache = True
        else:
            self._preferences.cleanTodoistCache = False

    def __onTaskStrategyChanges(self, event: CommandEvent):

        selection: str = event.GetString()
        strategy:  TodoistTaskCreationStrategy = TodoistTaskCreationStrategy(selection)

        self._preferences.taskCreationStrategy = strategy

        if strategy == TodoistTaskCreationStrategy.PROJECT_BY_REPOSITORY:
            self._parentProjectNameContainer.textControlEnabled(False)
        else:
            self._parentProjectNameContainer.textControlEnabled(True)
