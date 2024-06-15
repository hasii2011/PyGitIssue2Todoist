
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ID_ANY

from wx import Window
from wx import App as wxApp

from pygitissue2todoist.general.Resources import Resources

from pygitissue2todoist.ui.ApplicationFrame import ApplicationFrame


class WxApplication(wxApp):

    def __init__(self, redirect: bool):
        super().__init__(redirect)

        self.logger: Logger           = cast(Logger, None)
        self._frame: ApplicationFrame = cast(ApplicationFrame, None)

    def OnInit(self) -> bool:

        self.logger = getLogger(__name__)

        self._frame = ApplicationFrame(cast(Window, None), ID_ANY, Resources.CANONICAL_APPLICATION_NAME)

        self._frame.Show(True)
        self.SetTopWindow(self._frame)

        self.logger.info(f'Application Initialization Complete')

        return True
