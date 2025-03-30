

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

from wx.lib.ClickableHtmlWindow import PyClickableHtmlWindow

from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel

from pygitissue2todoist.general.ResourceTextType import ResourceTextType
from pygitissue2todoist.general.Resources import Resources


class DlgHelp(SizedDialog):

    def __init__(self, parent: Window, wxID: int = wxNewIdRef()):

        super().__init__(parent, wxID, 'Helpful Hints', style=DEFAULT_DIALOG_STYLE)

        self.Center(BOTH)
        pane: SizedPanel = self.GetContentsPane()
        pane.SetSizerType('horizontal')

        self._htmlWindow: PyClickableHtmlWindow = self._createHTMLPanel(sizedPanel=pane)
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(OK))

        self.Fit()
        self.SetMinSize(self.GetSize())
        #
        self.Bind(EVT_BUTTON, self.__onCmdOk, id=ID_OK)
        self.Bind(EVT_CLOSE,  self.__onCmdOk)

    def _createHTMLPanel(self, sizedPanel: SizedPanel) -> PyClickableHtmlWindow:

        htmlPanel: SizedPanel = SizedPanel(parent=sizedPanel, id=ID_ANY)
        htmlPanel.SetSizerType('horizontal')

        htmlPanel.SetSizerProps(expand=True)

        htmlSize:  Size = Size(width=440, height=210)
        htmlWindow: PyClickableHtmlWindow = PyClickableHtmlWindow(parent=htmlPanel, ID=ID_ANY, size=htmlSize, style=NO_FULL_REPAINT_ON_RESIZE)

        helpText: str = Resources.retrieveResourceText(ResourceTextType.SIMPLE_HELP)
        htmlWindow.SetPage(helpText)

        return htmlWindow

    def __onCmdOk(self, event: CommandEvent):
        event.Skip(skip=True)
        self.SetReturnCode(OK)
        self.EndModal(OK)
