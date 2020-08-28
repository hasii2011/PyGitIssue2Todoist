
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ID_ANY

from wx import Window
from wx import App as wxApp

from gittodoistclone.ui.ApplicationFrame import ApplicationFrame


class ClonerApplication(wxApp):

    def __init__(self, redirect: bool):
        super().__init__(redirect)

    def OnInit(self) -> bool:

        self.logger: Logger = getLogger(__name__)

        self._frame: ApplicationFrame = ApplicationFrame(cast(Window, None), ID_ANY, "Git Issue Clone to Todoist")

        self._frame.Show(True)
        self.SetTopWindow(self._frame)

        self.logger.info(f'Exit OnInit()')

        return True
