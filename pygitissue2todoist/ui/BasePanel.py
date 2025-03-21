
from abc import ABCMeta
from abc import abstractmethod

from os import sep as osSep

from wx import SYS_COLOUR_BACKGROUND
from wx import SYS_COLOUR_LISTBOXTEXT

from wx import Colour
from wx import Window
from wx import SystemSettings

from wx.lib.sized_controls import SizedPanel


class MyMetaBasePanel(ABCMeta, type(SizedPanel)):        # type: ignore
    """
    I have know idea why this works:
    https://stackoverflow.com/questions/66591752/metaclass-conflict-when-trying-to-create-a-python-abstract-class-that-also-subcl
    """
    pass


class BasePanel(SizedPanel):

    __metaclass__ = MyMetaBasePanel

    PROPORTION_NOT_CHANGEABLE: int = 0
    PROPORTION_CHANGEABLE:     int = 1

    RESOURCES_PACKAGE_NAME: str = 'pygitissue2todoist.resources'
    RESOURCES_PATH:         str = f'pygitissue2todoist{osSep}resources'

    RESOURCE_ENV_VAR:       str = 'RESOURCEPATH'

    def __init__(self, parent: Window):

        super().__init__(parent)

        self._bkColor:   Colour = SystemSettings.GetColour(SYS_COLOUR_BACKGROUND)
        self._textColor: Colour = SystemSettings.GetColour(SYS_COLOUR_LISTBOXTEXT)

    @abstractmethod
    def _layoutContent(self, parent: 'BasePanel'):
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
