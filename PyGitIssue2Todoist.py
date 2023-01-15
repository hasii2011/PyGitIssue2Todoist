
from logging import Logger
from logging import getLogger

import logging.config

from json import load as jsonLoad

from pathlib import Path

from gittodoistclone.general.Preferences import Preferences
from gittodoistclone.general.Resources import Resources
from gittodoistclone.general.Version import Version

from gittodoistclone.ui.WxApplication import WxApplication


class PyGitIssue2Todoist:


    JSON_LOGGING_CONFIG_FILENAME: str = "loggingConfiguration.json"

    def __init__(self):

        self._setupSystemLogging()
        self.logger: Logger = getLogger(__name__)

        Preferences.determinePreferencesLocation()
        configFile: Path = Path(Preferences.getPreferencesLocation())
        #
        # Will create a default one if necessary
        #
        if configFile.exists() is False:
            self._preferences = Preferences()

    def startApp(self):

        app: WxApplication = WxApplication(redirect=False)
        app.MainLoop()

    def displayVersionInformation(self):
        import wx
        import sys
        import platform

        print("Versions: ")
        print(f"{Resources.CANONICAL_APPLICATION_NAME}:  {Version().applicationVersion}")
        print(f'Platform: {platform.platform()}')
        print(f'    System:       {platform.system()}')
        print(f'    Version:      {platform.version()}')
        print(f'    Release:      {platform.release()}')

        print(f'WxPython: {wx.__version__}')
        print(f'Python:   {sys.version.split(" ")[0]}')

        # noinspection PyUnreachableCode
        if __debug__:
            print('Assertions are turned on')
        else:
            print('Assertions are turned off')

    def _setupSystemLogging(self):

        configFilePath: str = Resources.retrieveResourcePath(PyGitIssue2Todoist.JSON_LOGGING_CONFIG_FILENAME)

        with open(configFilePath, 'r') as loggingConfigurationFile:
            configurationDictionary = jsonLoad(loggingConfigurationFile)

        logging.config.dictConfig(configurationDictionary)
        logging.logProcesses = False
        logging.logThreads   = False


if __name__ == "__main__":

    print(f"Starting {Resources.CANONICAL_APPLICATION_NAME}")

    issueCloner: PyGitIssue2Todoist = PyGitIssue2Todoist()
    issueCloner.displayVersionInformation()
    issueCloner.startApp()
