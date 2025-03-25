
from logging import Logger
from logging import getLogger

from wx import DEFAULT_FRAME_STYLE
from wx import FRAME_FLOAT_ON_PARENT
from wx import Size
from wx import StatusBar

from wx.lib.sized_controls import SizedFrame
from wx.lib.sized_controls import SizedPanel

from pygitissue2todoist.ui.panels.OwnerIssuesGitHubPanel import OwnerIssuesGitHubPanel

from pygitissue2todoist.ui.eventengine.EventEngine import EventEngine
from pygitissue2todoist.ui.eventengine.IEventEngine import IEventEngine


class OwnerFrame(SizedFrame):

    def __init__(self):

        frameStyle: int   = DEFAULT_FRAME_STYLE | FRAME_FLOAT_ON_PARENT
        appSize:    Size  = Size(width=400, height=600)

        super().__init__(parent=None, title='Test Panel', size=appSize, style=frameStyle)

        self.logger: Logger = getLogger(__name__)

        self.GetContentsPane().SetSizerType('horizontal')
        self.GetContentsPane().SetSizerProps(expand=True, proportion=1)

        self._eventEngine: IEventEngine = EventEngine(listeningWindow=self)

        self._status: StatusBar = self.CreateStatusBar()

        self._testPanel: OwnerIssuesGitHubPanel = self._layoutApplicationContentArea()

        self._status.SetStatusText('Ready!')

    def _layoutApplicationContentArea(self) -> OwnerIssuesGitHubPanel:

        sizedPanel: SizedPanel              = self.GetContentsPane()
        testPanel:  OwnerIssuesGitHubPanel  = OwnerIssuesGitHubPanel(sizedPanel, eventEngine=self._eventEngine)

        return testPanel
