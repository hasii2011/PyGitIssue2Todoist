
from typing import cast

from sys import exit as sysExit

from pathlib import Path

from wx import OK
from wx import DEFAULT_FRAME_STYLE
from wx import ID_ANY

from wx import App
from wx import Frame

from gittodoistclone.general.Preferences import Preferences
from gittodoistclone.ui.dialogs.DlgConfigure import DlgConfigure


class ConfigurationApplication(App):
    """
    Invoking the configuration dialog will instantiate the Preferences singleton
    The Preferences singleton detects that the configuration file exists and will create a default one
    """

    def OnInit(self):

        topFrame: Frame = Frame(parent=None, id=ID_ANY, title="Configure gittodoistclone", size=(300, 200), style=DEFAULT_FRAME_STYLE)
        topFrame.Show(False)

        self.SetTopWindow(topFrame)
        self._topFrame: Frame = topFrame

        self._showConfigurationDialog()
        return True

    def _showConfigurationDialog(self):

        with DlgConfigure(self._topFrame) as dlg:
            dlg: DlgConfigure = cast(DlgConfigure, dlg)
            if dlg.ShowModal() == OK:
                print(f'Configuration Complete')
                self._topFrame.Close()
                self.Destroy()
            else:
                print(f'Configuration is incomplete')

                emptyPreferencesFile: Path = Path(Preferences.getPreferencesLocation())
                emptyPreferencesFile.unlink()

                sysExit()  # brutal !!
