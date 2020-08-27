
from logging import Logger
from logging import getLogger

import logging.config

from os import sep as osSep

from json import load as jsonLoad

from pkg_resources import resource_filename

from gittodoistclone.general.Preferences import Preferences
from gittodoistclone.ui.ClonerApplication import ClonerApplication


class PyGitIssueClone:

    MADE_UP_PRETTY_MAIN_NAME:     str = "Python Github Issue Clone"

    JSON_LOGGING_CONFIG_FILENAME: str = "loggingConfiguration.json"

    RESOURCES_PACKAGE_NAME: str = 'gittodoistclone.resources'
    RESOURCES_PATH:         str = f'gittodoistclone{osSep}resources'

    RESOURCE_ENV_VAR:       str = 'RESOURCEPATH'

    def __init__(self):

        self._setupSystemLogging()
        self.logger: Logger = getLogger(__name__)

        Preferences.determinePreferencesLocation()

    def startApp(self):

        app: ClonerApplication = ClonerApplication(redirect=False)
        app.MainLoop()

    def configurationFileExists(self) -> bool:

        ans: bool = True

        return ans

    @classmethod
    def retrieveResourcePath(cls, bareFileName: str) -> str:

        # Use this method in Python 3.9
        # from importlib_resources import files
        # configFilePath: str  = files('org.pyut.resources').joinpath(Pyut.JSON_LOGGING_CONFIG_FILENAME)

        try:
            fqFileName: str = resource_filename(PyGitIssueClone.RESOURCES_PACKAGE_NAME, bareFileName)
        except (ValueError, Exception):
            #
            # Maybe we are in an app
            #
            from os import environ
            pathToResources: str = environ.get(f'{PyGitIssueClone.RESOURCE_ENV_VAR}')
            fqFileName:      str = f'{pathToResources}/{PyGitIssueClone.RESOURCES_PATH}/{bareFileName}'

        return fqFileName

    def _setupSystemLogging(self):

        configFilePath: str = PyGitIssueClone.retrieveResourcePath(PyGitIssueClone.JSON_LOGGING_CONFIG_FILENAME)

        with open(configFilePath, 'r') as loggingConfigurationFile:
            configurationDictionary = jsonLoad(loggingConfigurationFile)

        logging.config.dictConfig(configurationDictionary)
        logging.logProcesses = False
        logging.logThreads   = False


if __name__ == "__main__":

    print(f"Starting {PyGitIssueClone.MADE_UP_PRETTY_MAIN_NAME}")

    issueCloner: PyGitIssueClone = PyGitIssueClone()
    issueCloner.startApp()
