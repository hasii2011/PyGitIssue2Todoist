

from wx import EVT_BUTTON
from wx import EVT_CLOSE
from wx import ID_ANY
from wx import ID_OK
from wx import NO_FULL_REPAINT_ON_RESIZE
from wx import DEFAULT_DIALOG_STYLE
from wx import BOTH
from wx import OK

from wx import CommandEvent
from wx import Size
from wx import Window

from wx import NewIdRef as wxNewIdRef

from wx.html import HtmlWindow

from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel

from gittodoistclone.general.ResourceTextType import ResourceTextType
from gittodoistclone.general.Resources import Resources


class DlgHelp(SizedDialog):

    def __init__(self, parent: Window, wxID: int = wxNewIdRef()):

        super().__init__(parent, wxID, 'Helpful Hints', style=DEFAULT_DIALOG_STYLE)

        self.Center(BOTH)
        pane: SizedPanel = self.GetContentsPane()
        pane.SetSizerType('horizontal')
        self._createHTMLPanel(sizedPanel=pane)
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(OK))

        self.Fit()
        self.SetMinSize(self.GetSize())

        self.Bind(EVT_BUTTON, self.__onCmdOk, id=ID_OK)
        self.Bind(EVT_CLOSE,  self.__onCmdOk)

    def _createHTMLPanel(self, sizedPanel: SizedPanel):

        htmlPanel: SizedPanel = SizedPanel(parent=sizedPanel, id=ID_ANY)
        htmlPanel.SetSizerType('horizontal')

        # noinspection PyUnresolvedReferences
        htmlPanel.SetSizerProps(expand=True)

        htmlSize:  Size = Size(width=440, height=128)
        self._html = HtmlWindow(parent=htmlPanel, id=ID_ANY, size=htmlSize, style=NO_FULL_REPAINT_ON_RESIZE)

        helpText: str = Resources.retrieveResourceText(ResourceTextType.SIMPLE_HELP)
        self._html.SetPage(helpText)

    def __onCmdOk(self, event: CommandEvent):
        event.Skip(skip=True)
        self.SetReturnCode(OK)
        self.EndModal(OK)
