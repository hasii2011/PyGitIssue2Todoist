
from typing import Tuple
from typing import Dict
from typing import cast

from logging import Logger
from logging import getLogger

from sys import platform

from os import getenv
from os import sep as osSep

from configparser import ConfigParser

from gittodoistclone.general.GitHubURLOption import GitHubURLOption
from gittodoistclone.general.Singleton import Singleton

from gittodoistclone.general.exceptions.InvalidPreference import InvalidPreference
from gittodoistclone.general.exceptions.PreferencesLocationNotSet import PreferencesLocationNotSet

from gittodoistclone.general.Resources import Resources

PREFERENCES_NAME_VALUES = Dict[str, str]


class Preferences(Singleton):
    """
    If the Preferences singleton detects that the configuration file does not exist it will create a default one
    """
    THE_GREAT_MAC_PLATFORM: str = 'darwin'
    # Take canonical name and lowercase the first later to make the dot file
    PREFERENCES_FILE_NAME:  str = (
        f'.{Resources.CANONICAL_APPLICATION_NAME[0].lower()}'
        f'{Resources.CANONICAL_APPLICATION_NAME[1:]}'
        f'.ini'
    )

    DEFAULT_APP_WIDTH:  int = 1024
    DEFAULT_APP_HEIGHT: int = 768
    NO_DEFAULT_X:       int = -1
    NO_DEFAULT_Y:       int = -1

    MAIN_SECTION:    str = 'Main'

    GITHUB_SECTION:  str = 'GitHub'
    TODOIST_SECTION: str = 'Todoist'

    TODOIST_API_TOKEN_KEY: str = 'todoist_api_token'
    GITHUB_API_TOKEN_KEY:  str = 'github_api_token'
    GITHUB_USER_NAME_KEY:  str = 'github_user_name'

    STARTUP_X:      str = 'startup_x'
    STARTUP_Y:      str = 'startup_y'
    STARTUP_WIDTH:  str = 'startup_width'
    STARTUP_HEIGHT: str = 'startup_height'

    GITHUB_URL_OPTION:   str = 'github_url_option'

    CLEAN_TODOIST_CACHE:    str = 'clean_todoist_cache'
    SINGLE_TODOIST_PROJECT: str = 'single_todoist_project'
    TODOIST_PROJECT_NAME:   str = 'todoist_project_name'

    MAIN_PREFERENCES: PREFERENCES_NAME_VALUES = {
        STARTUP_WIDTH:             str(DEFAULT_APP_WIDTH),
        STARTUP_HEIGHT:            str(DEFAULT_APP_HEIGHT),
        STARTUP_X:                 str(NO_DEFAULT_X),
        STARTUP_Y:                 str(NO_DEFAULT_Y),
    }

    GITHUB_PREFERENCES: PREFERENCES_NAME_VALUES = {
        GITHUB_API_TOKEN_KEY: 'PutYourGitHubKeyHere',
        GITHUB_USER_NAME_KEY: 'PutYourGitHubUserNameHere',
        GITHUB_URL_OPTION:    GitHubURLOption.HyperLinkedTaskName.value,
    }

    TODOIST_PREFERENCES: PREFERENCES_NAME_VALUES = {
        TODOIST_API_TOKEN_KEY:  'PutYourTodoistKeyHere',
        CLEAN_TODOIST_CACHE:    'True',
        SINGLE_TODOIST_PROJECT: 'True',
        TODOIST_PROJECT_NAME:   'Development'
    }

    preferencesFileLocationAndName: str = cast(str, None)
    """
    Class variable where we store our name
    """

    # noinspection PyAttributeOutsideInit
    def init(self):
        """
        """
        self.logger:  Logger = getLogger(__name__)

        self._config: ConfigParser = ConfigParser()
        self._loadConfiguration()

    @staticmethod
    def determinePreferencesLocation():
        """
        This method MUST (I repeat MUST) be called before
        attempting to instantiate the preferences Singleton
        """
        if platform == "linux2" or platform == "linux" or platform == Preferences.THE_GREAT_MAC_PLATFORM:
            Preferences.preferencesFileLocationAndName = getenv("HOME") + osSep + Preferences.PREFERENCES_FILE_NAME  # type: ignore
        else:
            Preferences.preferencesFileLocationAndName = Preferences.PREFERENCES_FILE_NAME

    @staticmethod
    def getPreferencesLocation():
        if Preferences.preferencesFileLocationAndName is None:
            raise PreferencesLocationNotSet()
        else:
            return Preferences.preferencesFileLocationAndName

    @property
    def todoistApiToken(self) -> str:
        return self._config.get(Preferences.TODOIST_SECTION, Preferences.TODOIST_API_TOKEN_KEY)

    @todoistApiToken.setter
    def todoistApiToken(self, newValue: str):
        self._config.set(Preferences.TODOIST_SECTION, Preferences.TODOIST_API_TOKEN_KEY, newValue)
        self.__saveConfig()

    @property
    def githubApiToken(self) -> str:
        return self._config.get(Preferences.GITHUB_SECTION, Preferences.GITHUB_API_TOKEN_KEY)

    @githubApiToken.setter
    def githubApiToken(self, newValue: str):
        self._config.set(Preferences.GITHUB_SECTION, Preferences.GITHUB_API_TOKEN_KEY, newValue)
        self.__saveConfig()

    @property
    def githubUserName(self) -> str:
        return self._config.get(Preferences.GITHUB_SECTION, Preferences.GITHUB_USER_NAME_KEY)

    @githubUserName.setter
    def githubUserName(self, newName: str):
        self._config.set(Preferences.GITHUB_SECTION, Preferences.GITHUB_USER_NAME_KEY, newName)
        self.__saveConfig()

    @property
    def appStartupPosition(self) -> Tuple[int, int]:

        x: int = self._config.getint(Preferences.MAIN_SECTION, Preferences.STARTUP_X)
        y: int = self._config.getint(Preferences.MAIN_SECTION, Preferences.STARTUP_Y)

        return x, y

    @appStartupPosition.setter
    def appStartupPosition(self, theNewValue: Tuple[int, int]):

        x: int = theNewValue[0]
        y: int = theNewValue[1]

        self._config.set(Preferences.MAIN_SECTION, Preferences.STARTUP_X, str(x))
        self._config.set(Preferences.MAIN_SECTION, Preferences.STARTUP_Y, str(y))

        self.__saveConfig()

    @property
    def startupWidth(self) -> int:
        width: int = self._config.getint(Preferences.MAIN_SECTION, Preferences.STARTUP_WIDTH)
        return width

    @startupWidth.setter
    def startupWidth(self, newWidth: int):
        self._config.set(Preferences.MAIN_SECTION, Preferences.STARTUP_WIDTH, str(newWidth))
        self.__saveConfig()

    @property
    def startupHeight(self) -> int:
        height: int = self._config.getint(Preferences.MAIN_SECTION, Preferences.STARTUP_HEIGHT)
        return height

    @startupHeight.setter
    def startupHeight(self, newHeight: int):
        self._config.set(Preferences.MAIN_SECTION, Preferences.STARTUP_HEIGHT, str(newHeight))
        self.__saveConfig()

    @property
    def githubURLOption(self) -> GitHubURLOption:
        strOption: str = self._config.get(Preferences.GITHUB_SECTION, Preferences.GITHUB_URL_OPTION)
        retValue:   GitHubURLOption = GitHubURLOption(strOption)
        return retValue

    @githubURLOption.setter
    def githubURLOption(self, newValue: GitHubURLOption):
        self._config.set(Preferences.GITHUB_SECTION, Preferences.GITHUB_URL_OPTION, newValue.value)
        self.__saveConfig()

    @property
    def cleanTodoistCache(self) -> bool:
        return self._config.getboolean(Preferences.TODOIST_SECTION, Preferences.CLEAN_TODOIST_CACHE)

    @cleanTodoistCache.setter
    def cleanTodoistCache(self, newValue: bool):
        self._config.set(Preferences.TODOIST_SECTION, Preferences.CLEAN_TODOIST_CACHE, str(newValue))
        self.__saveConfig()

    @property
    def singleTodoistProject(self) -> bool:
        return self._config.getboolean(Preferences.TODOIST_SECTION, Preferences.SINGLE_TODOIST_PROJECT)

    @singleTodoistProject.setter
    def singleTodoistProject(self, newValue: bool):
        self._config.set(Preferences.TODOIST_SECTION, Preferences.SINGLE_TODOIST_PROJECT, str(newValue))
        self.__saveConfig()

    @property
    def todoistProjectName(self) -> str:
        return self._config.get(Preferences.TODOIST_SECTION, Preferences.TODOIST_PROJECT_NAME)

    @todoistProjectName.setter
    def todoistProjectName(self, newValue: str):
        if newValue is None or newValue == '':
            invalidPreference: InvalidPreference = InvalidPreference()
            invalidPreference.preferenceName = 'parentProjectName'
            raise invalidPreference

        self._config.set(Preferences.TODOIST_SECTION, Preferences.TODOIST_PROJECT_NAME, newValue)
        self.__saveConfig()

    def _loadConfiguration(self):
        """
        Load preferences from configuration file
        """
        self.__ensureConfigurationFileExists()
        self._config.read(Preferences.getPreferencesLocation())
        self.__createNeededSectionsIfNecessary()
        # self.__createNeededConfigurationKeys()
        self.__createApplicationPreferences()
        self.__saveConfig()

    def __createNeededSectionsIfNecessary(self):

        self.__createSectionIfNecessary(Preferences.GITHUB_SECTION)
        self.__createSectionIfNecessary(Preferences.TODOIST_SECTION)
        self.__createSectionIfNecessary(Preferences.MAIN_SECTION)

    def __createSectionIfNecessary(self, sectionName: str):

        hasSection: bool = self._config.has_section(sectionName)
        self.logger.debug(f'hasSection: {hasSection} - {sectionName}')
        if hasSection is False:
            self._config.add_section(sectionName)

    def __createApplicationPreferences(self):

        for prefName in Preferences.MAIN_PREFERENCES.keys():
            if self._config.has_option(Preferences.MAIN_SECTION, prefName) is False:
                self.__addMissingMainPreference(prefName, Preferences.MAIN_PREFERENCES[prefName])

        # There is only a few GitHub preferences;  The other values are created as part of authentication
        for prefName in Preferences.GITHUB_PREFERENCES.keys():
            if self._config.has_option(Preferences.GITHUB_SECTION, prefName) is False:
                self.__addMissingGitHubPreference(prefName, Preferences.GITHUB_PREFERENCES[prefName])

        for prefName in Preferences.TODOIST_PREFERENCES.keys():
            if self._config.has_option(Preferences.TODOIST_SECTION, prefName) is False:
                self.__addMissingTodoistPreference(prefName, Preferences.TODOIST_PREFERENCES[prefName])

    def __addMissingMainPreference(self, preferenceName, value: str):
        self.__addMissingPreference(Preferences.MAIN_SECTION, preferenceName, value)

    def __addMissingGitHubPreference(self, preferenceName, value: str):
        self.__addMissingPreference(Preferences.GITHUB_SECTION, preferenceName, value)

    def __addMissingTodoistPreference(self, preferenceName: str, value: str):
        self.__addMissingPreference(Preferences.TODOIST_SECTION, preferenceName, value)

    def __addMissingPreference(self, sectionName: str, preferenceName: str, value: str):
        self._config.set(sectionName, preferenceName, value)
        self.__saveConfig()

    def __ensureConfigurationFileExists(self):

        # Make sure that the configuration file exists
        try:
            # noinspection PyUnusedLocal
            with open(Preferences.getPreferencesLocation(), "r") as f:
                pass
        except (ValueError, Exception):
            try:
                with open(Preferences.getPreferencesLocation(), "w") as newFile:
                    newFile.write("")
                    self.logger.warning(f'Preferences file re-created')
            except (ValueError, Exception) as e:
                self.logger.error(f"Error: {e}")
                return

    def __saveConfig(self):
        """
        Save configuration data to the configuration file
        """
        f = open(Preferences.getPreferencesLocation(), "w")
        self._config.write(f)
        f.close()
