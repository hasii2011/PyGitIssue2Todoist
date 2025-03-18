
from logging import Logger
from logging import getLogger

from sys import exit as sysExit

from wx import DEFAULT_FRAME_STYLE
from wx import OK

from wx import App
from wx import Frame

from pygitissue2todoist.general.Preferences import Preferences
from pygitissue2todoist.ui.dialogs.configuration.DlgConfigure import DlgConfigure

from tests.ProjectTestBase import ProjectTestBase


class DialogTestApp(App):

    FRAME_ID: int = 0xDeadBeef

    # noinspection PyAttributeOutsideInit
    def OnInit(self):

        ProjectTestBase.setUpLogging()
        self.logger: Logger = getLogger('TestADialog')
        frameTop: Frame = Frame(parent=None, id=DialogTestApp.FRAME_ID, title="Test A Dialog", size=(600, 400), style=DEFAULT_FRAME_STYLE)

        self.SetTopWindow(frameTop)
        self._frameTop = frameTop

        self.initTest()
        return True

    # noinspection SpellCheckingInspection
    def initTest(self):
        with DlgConfigure(self._frameTop) as dlg:

            if dlg.ShowModal() == OK:
                preferences: Preferences = Preferences()

                self.logger.info(f'{preferences.todoistAPIToken=}')
                self.logger.info(f'{preferences.gitHubUserName=}')
                self.logger.info(f'{preferences.gitHubAPIToken=}')
            else:
                self.logger.warning(f'Cancelled')

        self.logger.info(f"After dialog show")
        sysExit()   # brutal !!


testApp: App = DialogTestApp(redirect=False)

testApp.MainLoop()
