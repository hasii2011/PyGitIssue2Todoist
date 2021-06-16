
from typing import cast

from logging import Logger
from logging import getLogger

from sys import exit as sysExit

from wx import DEFAULT_FRAME_STYLE
from wx import OK

from wx import App
from wx import Frame

from gittodoistclone.general.Preferences import Preferences
from gittodoistclone.ui.dialogs.DlgConfigure import DlgConfigure

from tests.TestBase import TestBase


class TestADialog(App):

    FRAME_ID: int = 0xDeadBeef

    def OnInit(self):

        TestBase.setUpLogging()
        self.logger: Logger = getLogger('TestADialog')
        frameTop: Frame = Frame(parent=None, id=TestADialog.FRAME_ID, title="Test A Dialog", size=(600, 400), style=DEFAULT_FRAME_STYLE)
        # frameTop.Show(False)

        Preferences.determinePreferencesLocation()

        self.SetTopWindow(frameTop)
        self._frameTop = frameTop

        self.initTest()
        return True

    def initTest(self):

        with DlgConfigure(self._frameTop) as dlg:
            dlg: DlgConfigure = cast(DlgConfigure, dlg)
            if dlg.ShowModal() == OK:
                preferences: Preferences = Preferences()
                # self._frameTop.Close(force=True)
                self.logger.info(f'{preferences.todoistApiToken=}')
                self.logger.info(f'{preferences.githubUserName=}')
                self.logger.info(f'{preferences.githubApiToken=}')
            else:
                self.logger.warning(f'Cancelled')
                # self._frameTop.Close(force=True)

        self.logger.info(f"After dialog show")
        sysExit()   # brutal !!


testApp: App = TestADialog(redirect=False)

testApp.MainLoop()
