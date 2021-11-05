
from wx.lib.sized_controls import SizedPanel

from gittodoistclone.general.Preferences import Preferences


class PreferencesPanel(SizedPanel):

    def __init__(self, parent, *args, **kwargs):

        super().__init__(parent, *args, **kwargs)

        self._preferences: Preferences = Preferences()

    def _createControls(self):
        """
        Abstract method
        Creates the panel's controls and stashes them as private instance variables
        """
        pass

    def _setControlValues(self):
        """
        Set the default values on the controls.
        """
        pass
