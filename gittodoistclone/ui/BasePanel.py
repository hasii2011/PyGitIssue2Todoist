
from os import sep as osSep

from pkg_resources import resource_filename

from wx import Panel
from wx import SYS_COLOUR_BACKGROUND

from wx import SystemSettings
from wx import Colour

from wx import Window


class BasePanel(Panel):

    RESOURCES_PACKAGE_NAME: str = 'gittodoistclone.resources'
    RESOURCES_PATH:         str = f'gittodoistclone{osSep}resources'

    RESOURCE_ENV_VAR:       str = 'RESOURCEPATH'

    def __init__(self, parent: Window):

        super().__init__(parent)

        self._bkColor: Colour = SystemSettings.GetColour(SYS_COLOUR_BACKGROUND)

    @property
    def backgroundColor(self) -> Colour:
        return self._bkColor

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
