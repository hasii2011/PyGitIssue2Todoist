
from os import sep as osSep

from wx import SYS_COLOUR_BACKGROUND
from wx import SYS_COLOUR_LISTBOXTEXT

from wx import BoxSizer
from wx import Panel
from wx import Colour
from wx import Window
from wx import SystemSettings


class BasePanel(Panel):

    PROPORTION_NOT_CHANGEABLE: int = 0
    PROPORTION_CHANGEABLE:     int = 1

    RESOURCES_PACKAGE_NAME: str = 'gittodoistclone.resources'
    RESOURCES_PATH:         str = f'gittodoistclone{osSep}resources'

    RESOURCE_ENV_VAR:       str = 'RESOURCEPATH'

    def __init__(self, parent: Window):

        super().__init__(parent)

        self._bkColor:   Colour = SystemSettings.GetColour(SYS_COLOUR_BACKGROUND)
        self._textColor: Colour = SystemSettings.GetColour(SYS_COLOUR_LISTBOXTEXT)

    def _layoutContent(self) -> BoxSizer:
        """
        Child class must override this method

        Returns:    The container that has panel contents
        """
        pass

    @property
    def backgroundColor(self) -> Colour:
        return self._bkColor

    @property
    def textColor(self) -> Colour:
        return self._textColor
