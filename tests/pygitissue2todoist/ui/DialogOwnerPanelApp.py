
from logging import Logger
from logging import getLogger

from wx import App

from tests.ProjectTestBase import ProjectTestBase

from tests.pygitissue2todoist.ui.OwnerFrame import OwnerFrame


class DialogOwnerPanelApp(App):

    # noinspection PyAttributeOutsideInit
    def OnInit(self):

        ProjectTestBase.setUpLogging()

        self.logger: Logger = getLogger(__name__)

        sizedFrame: OwnerFrame = OwnerFrame()

        self.SetTopWindow(sizedFrame)
        sizedFrame.Show(True)

        self._sizedFrame: OwnerFrame = sizedFrame

        # self.initTest()

        return True


if __name__ == "__main__":
    testApp: App = DialogOwnerPanelApp()

    testApp.MainLoop()
