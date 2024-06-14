
from codeallybasic.UnitTestBase import UnitTestBase

JSON_LOGGING_CONFIG_FILENAME: str = "testLoggingConfiguration.json"
TEST_DIRECTORY:               str = 'tests'


class ProjectTestBase(UnitTestBase):

    RESOURCES_PACKAGE_NAME:              str = 'tests.resources'
    RESOURCES_TEST_CLASSES_PACKAGE_NAME: str = 'tests.testclass'
