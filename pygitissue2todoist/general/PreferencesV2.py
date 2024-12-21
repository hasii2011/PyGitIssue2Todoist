
from typing import cast

from logging import Logger
from logging import getLogger

from codeallybasic.ConfigurationProperties import ConfigurationNameValue
from codeallybasic.ConfigurationProperties import PropertyName
from codeallybasic.ConfigurationProperties import Section
from codeallybasic.ConfigurationProperties import SectionName
from codeallybasic.ConfigurationProperties import Sections
from codeallybasic.ConfigurationProperties import configurationGetter
from codeallybasic.ConfigurationProperties import configurationSetter

from codeallybasic.Dimensions import Dimensions
from codeallybasic.Position import Position
from codeallybasic.SingletonV3 import SingletonV3
from codeallybasic.SecureConversions import SecureConversions
from codeallybasic.ConfigurationProperties import ConfigurationProperties

from pygitissue2todoist.general.GitHubURLOption import GitHubURLOption
from pygitissue2todoist.general.Resources import Resources

DEFAULT_APP_WIDTH:  int = 1024
DEFAULT_APP_HEIGHT: int = 768

DEFAULT_STARTUP_SIZE:         Dimensions = Dimensions(width=DEFAULT_APP_WIDTH, height=DEFAULT_APP_HEIGHT)
DEFAULT_TODOIST_PROJECT_NAME: str        = 'Development'

MAIN_SECTION_NAME:    SectionName = SectionName('Main')
GITHUB_SECTION_NAME:  SectionName = SectionName('GitHub')
TODOIST_SECTION_NAME: SectionName = SectionName('Todoist')


SECTION_MAIN: Section = Section(
    [

        ConfigurationNameValue(name=PropertyName('startupPosition'), defaultValue=Position(32, 32).__str__()),
        ConfigurationNameValue(name=PropertyName('startupSize'),     defaultValue=DEFAULT_STARTUP_SIZE.__str__()),

    ]
)


SECTION_GITHUB: Section = Section(
    [
        ConfigurationNameValue(name=PropertyName('gitHubAPIToken'),  defaultValue='PutYourGitHubKeyHere'),
        ConfigurationNameValue(name=PropertyName('gitHubUserName'),  defaultValue='PutYourGitHubUserNameHere'),
        ConfigurationNameValue(name=PropertyName('gitHubURLOption'), defaultValue=GitHubURLOption.HyperLinkedTaskName.value),
    ]
)

SECTION_TODOIST: Section = Section(
    [
        ConfigurationNameValue(name=PropertyName('todoistAPIToken'),      defaultValue='PutYourTodoistKeyHere'),
        ConfigurationNameValue(name=PropertyName('cleanTodoistCache'),    defaultValue='True'),
        ConfigurationNameValue(name=PropertyName('singleTodoistProject'), defaultValue='True'),
        ConfigurationNameValue(name=PropertyName('todoistProjectName'),   defaultValue=DEFAULT_TODOIST_PROJECT_NAME),
        ConfigurationNameValue(name=PropertyName('assignmentMode'), defaultValue='True'),
    ]
)

CONFIGURATION_SECTIONS: Sections = Sections(
    {
        MAIN_SECTION_NAME:    SECTION_MAIN,
        GITHUB_SECTION_NAME:  SECTION_GITHUB,
        TODOIST_SECTION_NAME: SECTION_TODOIST,
    }
)


class PreferencesV2(ConfigurationProperties, metaclass=SingletonV3):

    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        baseFileName: str = f'{Resources.CANONICAL_APPLICATION_NAME.lower()}.ini'
        super().__init__(baseFileName=baseFileName,
                         moduleName=Resources.CANONICAL_APPLICATION_NAME.lower(), sections=CONFIGURATION_SECTIONS)

        self._configParser.optionxform = str        # type: ignore
        self._loadConfiguration()

    @property
    @configurationGetter(sectionName=MAIN_SECTION_NAME, deserializeFunction=Position.deSerialize)
    def startupPosition(self) -> Position:
        return Position(0, 0)

    @startupPosition.setter
    @configurationSetter(sectionName=MAIN_SECTION_NAME)
    def startupPosition(self, newValue: Position):
        pass

    @property
    @configurationGetter(sectionName=MAIN_SECTION_NAME, deserializeFunction=Dimensions.deSerialize)
    def startupSize(self) -> Dimensions:
        return Dimensions(0, 0)

    @startupSize.setter
    @configurationSetter(sectionName=MAIN_SECTION_NAME)
    def startupSize(self, newValue: Dimensions):
        pass

    @property
    @configurationGetter(sectionName=GITHUB_SECTION_NAME)
    def gitHubAPIToken(self) -> str:
        return ''

    @gitHubAPIToken.setter
    @configurationSetter(sectionName=GITHUB_SECTION_NAME)
    def gitHubAPIToken(self, newValue: str):
        pass

    @property
    @configurationGetter(sectionName=GITHUB_SECTION_NAME)
    def gitHubUserName(self) -> str:
        return ''       # Value never used

    @gitHubUserName.setter
    @configurationSetter(sectionName=GITHUB_SECTION_NAME)
    def gitHubUserName(self, newValue: str):
        pass

    @property
    @configurationGetter(sectionName=GITHUB_SECTION_NAME, deserializeFunction=GitHubURLOption.deSerialize)
    def gitHubURLOption(self) -> GitHubURLOption:
        return cast(GitHubURLOption, None)

    @gitHubURLOption.setter
    @configurationSetter(sectionName=GITHUB_SECTION_NAME, isEnum=True)
    def gitHubURLOption(self, newValue: GitHubURLOption):
        pass

    @property
    @configurationGetter(sectionName=TODOIST_SECTION_NAME, deserializeFunction=SecureConversions.secureBoolean)
    def cleanTodoistCache(self) -> bool:
        return False    # Value never used

    @cleanTodoistCache.setter
    @configurationSetter(sectionName=TODOIST_SECTION_NAME)
    def cleanTodoistCache(self, newValue: bool):
        pass

    @property
    @configurationGetter(sectionName=TODOIST_SECTION_NAME, deserializeFunction=SecureConversions.secureBoolean)
    def singleTodoistProject(self) -> bool:
        return False    # Value never used

    @singleTodoistProject.setter
    @configurationSetter(sectionName=TODOIST_SECTION_NAME)
    def singleTodoistProject(self, newValue: bool):
        pass

    @property
    @configurationGetter(sectionName=TODOIST_SECTION_NAME)
    def todoistProjectName(self) -> str:
        return DEFAULT_TODOIST_PROJECT_NAME     # Unused

    @todoistProjectName.setter
    @configurationSetter(sectionName=TODOIST_SECTION_NAME)
    def todoistProjectName(self, newValue: str):
        pass

    @property
    @configurationGetter(sectionName=TODOIST_SECTION_NAME, deserializeFunction=SecureConversions.secureBoolean)
    def assignmentMode(self) -> bool:
        return True
    
    @assignmentMode.setter
    @configurationSetter(sectionName=TODOIST_SECTION_NAME)
    def assignmentMode(self, newValue: bool):
        pass


    @property
    @configurationGetter(sectionName=TODOIST_SECTION_NAME)
    def todoistAPIToken(self) -> str:
        return ''       # value never returned

    @todoistAPIToken.setter
    @configurationSetter(sectionName=TODOIST_SECTION_NAME)
    def todoistAPIToken(self, newValue: str):
        pass
