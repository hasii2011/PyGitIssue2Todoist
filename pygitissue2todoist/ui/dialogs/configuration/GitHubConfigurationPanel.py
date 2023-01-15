from typing import List
from typing import cast

from wx import CommandEvent
from wx import DefaultPosition
from wx import DefaultSize
from wx import EVT_RADIOBOX
from wx import ID_ANY
from wx import NOT_FOUND
from wx import RA_SPECIFY_COLS
from wx import RadioBox

from pygitissue2todoist.general.GitHubURLOption import GitHubURLOption
from pygitissue2todoist.ui.dialogs.configuration.AbstractConfigurationPanel import AbstractConfigurationPanel

URL_OPTIONS: List[str] = [GitHubURLOption.DoNotAdd.value,
                          GitHubURLOption.AddAsDescription.value,
                          GitHubURLOption.AddAsComment.value,
                          GitHubURLOption.HyperLinkedTaskName.value
                          ]


class GitHubConfigurationPanel(AbstractConfigurationPanel):

    def __init__(self, parent, *args, **kwargs):
        """
        """
        self._URLOption:  RadioBox = cast(RadioBox, None)

        super().__init__(parent, *args, **kwargs)

        self.SetSizerType('vertical')

        self.Bind(EVT_RADIOBOX, self.__URLOptionChanged, self._URLOption)

    def _createControls(self):
        """
        Creates the panel's controls and stashes them as private instance variables
        """
        self._URLOption = RadioBox(parent=self, id=ID_ANY,
                                   label="Include GitHub Issue URL",
                                   pos=DefaultPosition,
                                   size=DefaultSize,
                                   choices=URL_OPTIONS,
                                   majorDimension=1,
                                   style=RA_SPECIFY_COLS
                                   )

    def _setControlValues(self):
        """
        Set the current configuration values on the controls.
        """
        idx: int = self._URLOption.FindString(self._preferences.githubURLOption.value, bCase=False)
        assert idx != NOT_FOUND, "Developer Error; Enumeration may have changed"
        self._URLOption.SetSelection(idx)

    def __URLOptionChanged(self, event: CommandEvent):

        selectedIdx: int = event.GetInt()
        print(f'__onGitHubURLOptionChanged - {selectedIdx}')

        selectedOption: str             = self._URLOption.GetString(selectedIdx)
        newOption:      GitHubURLOption = GitHubURLOption(selectedOption)

        self._preferences.githubURLOption = newOption
