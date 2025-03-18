
from logging import Logger
from logging import getLogger

from codeallybasic.Position import Position
from codeallybasic.Dimensions import Dimensions
from codeallybasic.SingletonV3 import SingletonV3
from codeallybasic.DynamicConfiguration import DynamicConfiguration
from codeallybasic.DynamicConfiguration import KeyName
from codeallybasic.DynamicConfiguration import SectionName
from codeallybasic.DynamicConfiguration import Sections
from codeallybasic.DynamicConfiguration import ValueDescription
from codeallybasic.DynamicConfiguration import ValueDescriptions
from codeallybasic.SecureConversions import SecureConversions

from pygitissue2todoist.general.GitHubURLOption import GitHubURLOption

from pygitissue2todoist.general.Resources import Resources


DEFAULT_APP_WIDTH:    int        = 1024
DEFAULT_APP_HEIGHT:   int        = 768
DEFAULT_POSITION:     str        = Position(32, 32).__str__()
DEFAULT_STARTUP_SIZE: Dimensions = Dimensions(width=DEFAULT_APP_WIDTH, height=DEFAULT_APP_HEIGHT).__str__()

DEFAULT_TODOIST_PROJECT_NAME: str = 'Development'


SECTION_MAIN: ValueDescriptions = ValueDescriptions(
    {
        KeyName('startupPosition'): ValueDescription(defaultValue=DEFAULT_POSITION,     deserializer=Position.deSerialize),
        KeyName('startupSize'):     ValueDescription(defaultValue=DEFAULT_STARTUP_SIZE, deserializer=Dimensions.deSerialize),
    }
)

SECTION_GITHUB: ValueDescriptions = ValueDescriptions(
    {
        KeyName('gitHubAPIToken'):  ValueDescription(defaultValue='Put Your GitHub API Token Here'),
        KeyName('gitHubUserName'):  ValueDescription(defaultValue='Put Your GitHub User Name Here'),
        KeyName('gitHubURLOption'): ValueDescription(defaultValue=GitHubURLOption.HyperLinkedTaskName.value, deserializer=GitHubURLOption, enumUseValue=True),
    }
)

TODOIST_SECTION: ValueDescriptions = ValueDescriptions(
    {
        KeyName('todoistAPIToken'):      ValueDescription(defaultValue='Put Your Todoist API Token Here'),
        KeyName('cleanTodoistCache'):    ValueDescription(defaultValue='True', deserializer=SecureConversions.secureBoolean),
        KeyName('singleTodoistProject'): ValueDescription(defaultValue='True', deserializer=SecureConversions.secureBoolean),
        KeyName('todoistProjectName'):   ValueDescription(defaultValue=DEFAULT_TODOIST_PROJECT_NAME),
    }
)

CONFIGURATION_SECTIONS: Sections = Sections(
    {
        SectionName('Main'):    SECTION_MAIN,
        SectionName('GitHub'):  SECTION_GITHUB,
        SectionName('Todoist'): TODOIST_SECTION,
    }
)


class Preferences(DynamicConfiguration, metaclass=SingletonV3):
    def __init__(self):
        self._logger: Logger = getLogger(__name__)

        baseFileName: str = f'{Resources.CANONICAL_APPLICATION_NAME.lower()}.ini'
        moduleName:   str = f'{Resources.CANONICAL_APPLICATION_NAME.lower()}'

        super().__init__(baseFileName=baseFileName, moduleName=moduleName, sections=CONFIGURATION_SECTIONS)
