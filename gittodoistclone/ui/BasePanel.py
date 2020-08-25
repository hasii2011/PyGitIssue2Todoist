
from os import sep as osSep

from pkg_resources import resource_filename

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

    @classmethod
    def retrieveResourcePath(cls, bareFileName: str) -> str:

        # Use this method in Python 3.9
        # from importlib_resources import files
        # configFilePath: str  = files('org.pyut.resources').joinpath(Pyut.JSON_LOGGING_CONFIG_FILENAME)

        try:
            fqFileName: str = resource_filename(BasePanel.RESOURCES_PACKAGE_NAME, bareFileName)
        except (ValueError, Exception):
            #
            # Maybe we are in an app
            #
            from os import environ
            pathToResources: str = environ.get(f'{BasePanel.RESOURCE_ENV_VAR}')
            fqFileName:      str = f'{pathToResources}{osSep}{BasePanel.RESOURCES_PATH}{osSep}{bareFileName}'

        return fqFileName
