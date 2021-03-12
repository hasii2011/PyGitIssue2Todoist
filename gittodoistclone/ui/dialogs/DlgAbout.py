
from wx import ALIGN_CENTER
from wx import ALIGN_LEFT
from wx import ALL
from wx import BOTH
from wx import CAPTION
from wx import EVT_BUTTON
from wx import EVT_CLOSE
from wx import FONTFAMILY_DEFAULT
from wx import HORIZONTAL
from wx import ID_ANY
from wx import DefaultPosition
from wx import ID_OK
from wx import LI_HORIZONTAL
from wx import OK
from wx import VERTICAL
from wx import WHITE

from wx import Sizer
from wx import StaticLine
from wx import StaticText
from wx import Font
from wx import Dialog
from wx import BoxSizer
from wx import CommandEvent
from wx import StaticBitmap
from wx import Window
from wx import Size

from wx import NewIdRef as wxNewIdRef

from gittodoistclone.general.Version import Version
from gittodoistclone.resources import AboutDialogBaseLogo


class DlgAbout(Dialog):

    def __init__(self, parent: Window, wxID: int = wxNewIdRef()):

        super().__init__(parent, wxID, 'About', DefaultPosition, size=Size(width=390, height=250))

        self._versionFont: Font = self.GetFont()

        self._versionFont.SetFamily(FONTFAMILY_DEFAULT)

        self._version: Version = Version()  # Get the singleton

        dlgButtonsContainer: Sizer = self._createDialogButtonsContainer()

        # Main sizer
        mainSizer:   BoxSizer = BoxSizer(VERTICAL)
        dialogSizer: BoxSizer = self._createUpperDialog()

        mainSizer.Add(dialogSizer,         0, ALL | ALIGN_LEFT, 5)
        mainSizer.Add(dlgButtonsContainer, 0, ALL | ALIGN_CENTER, 5)

        # noinspection PyUnresolvedReferences
        self.SetAutoLayout(True)
        # noinspection PyUnresolvedReferences
        self.SetSizer(mainSizer)
        self.Center(BOTH)
        self.SetBackgroundColour(WHITE)

        self.Bind(EVT_BUTTON, self._onOk, id=ID_OK)
        self.Bind(EVT_CLOSE,  self._onOk)

    # noinspection PyUnusedLocal
    def _onOk(self, event: CommandEvent):
        """
        Handle user click on the OK button
        """
        self.EndModal(OK)

    def _createUpperDialog(self) -> BoxSizer:

        picture: StaticBitmap = StaticBitmap(self, ID_ANY, AboutDialogBaseLogo.embeddedImage.GetBitmap())

        dialogSizer:  BoxSizer = BoxSizer(HORIZONTAL)
        versionSizer: BoxSizer = self._createVersionsContainer()

        dialogSizer.Add(picture, 0, ALL | ALIGN_LEFT, 5)
        dialogSizer.Add(versionSizer, 0, ALL | ALIGN_LEFT, 5)

        return dialogSizer

    # noinspection PyArgumentList
    def _createVersionsContainer(self) -> BoxSizer:
        """
        The noinspection is set for the StaticText.SetFont() methods

        Returns:  The container
        """

        version: Version = self._version

        pyVersionText:      str = f'Python Version:   {version.pythonVersion}'
        wxVersionText:      str = f'WxPython Version: {version.wxPythonVersion}'
        pyGithubText:       str = f'PyGithub Version: {version.pyGithubVersion}'
        todoistVersionText: str = f'Todoist Version:  {version.todoistVersion}'

        appNameVersionText: str = f'{version.applicationName} - {version.applicationVersion}'

        appNameVersion:  StaticText = StaticText(self, ID_ANY, appNameVersionText,             style=CAPTION)
        longVersion:     StaticText = StaticText(self, ID_ANY, version.applicationLongVersion, style=CAPTION)
        appSeparator:    StaticLine = StaticLine(self, ID_ANY, style=LI_HORIZONTAL)
        pyVersion:       StaticText = StaticText(self, ID_ANY, pyVersionText,           style=CAPTION)
        wxVersion:       StaticText = StaticText(self, ID_ANY, wxVersionText,           style=CAPTION)
        pyGithubVersion: StaticText = StaticText(self, ID_ANY, pyGithubText,            style=CAPTION)
        todoistVersion:  StaticText = StaticText(self, ID_ANY, todoistVersionText,      style=CAPTION)

        versionSizer: BoxSizer = BoxSizer(VERTICAL)

        appNameVersion.SetFont(self._versionFont)
        longVersion.SetFont(self._versionFont)
        pyVersion.SetFont(self._versionFont)
        wxVersion.SetFont(self._versionFont)
        pyGithubVersion.SetFont(self._versionFont)
        todoistVersion.SetFont(self._versionFont)

        versionSizer.Add(appNameVersion,  0, ALL | ALIGN_LEFT, 1)
        versionSizer.Add(longVersion,     0, ALL | ALIGN_LEFT, 1)
        versionSizer.Add(appSeparator,    0, ALL | ALIGN_LEFT, 1)
        versionSizer.Add(pyVersion,       0, ALL | ALIGN_LEFT, 1)
        versionSizer.Add(wxVersion,       0, ALL | ALIGN_LEFT, 1)
        versionSizer.Add(pyGithubVersion, 0, ALL | ALIGN_LEFT, 1)
        versionSizer.Add(todoistVersion,  0, ALL | ALIGN_LEFT, 1)

        return versionSizer

    def _createDialogButtonsContainer(self, buttons=OK) -> Sizer:

        hs: Sizer = self.CreateSeparatedButtonSizer(buttons)

        return hs
