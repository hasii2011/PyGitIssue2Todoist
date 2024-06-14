
from typing import cast

from os import path as osPath
from os import remove as osRemove

from shutil import copyfile

from unittest import TestSuite
from unittest import main as unitTestMain

from pygitissue2todoist.general.exceptions.InvalidPreference import InvalidPreference

from pygitissue2todoist.general.Preferences import Preferences

from tests.ProjectTestBase import ProjectTestBase


BOGUS_TODOIST_API_TOKEN: str = '88888'


class TestPreferences(ProjectTestBase):
    """
    """
    BACKUP_SUFFIX: str = '.backup'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Preferences.determinePreferencesLocation()

    def setUp(self):
        super().setUp()

        self._backupPreferences()

    def tearDown(self):
        super().tearDown()

        self._restoreBackup()

    def testNoPreferencesExist(self):

        preferences: Preferences = Preferences()
        self.assertIsNotNone(preferences, 'Ouch.  Was not created')

    def testTodoistApiToken(self):

        preferences: Preferences = Preferences()

        saveTodoistApiToken = preferences.todoistApiToken
        preferences.todoistApiToken = BOGUS_TODOIST_API_TOKEN

        self.assertEqual(BOGUS_TODOIST_API_TOKEN, preferences.todoistApiToken, 'Uh oh, token did not change')

        preferences.todoistApiToken = saveTodoistApiToken

    def testSingleTodoistProjectFalse(self):
        preferences: Preferences = Preferences()
        preferences.singleTodoistProject = False
        self.assertFalse(preferences.singleTodoistProject, "Did not change to 'False'")

    def testSingleTodoistProjectTrue(self):
        preferences: Preferences = Preferences()
        preferences.singleTodoistProject = True
        self.assertTrue(preferences.singleTodoistProject, "Did not change to 'True'")

    def testTodoistProjectNameEmpty(self):
        self.assertRaises(InvalidPreference, lambda: self.__setTodoistProjectNameToEmpty())

    def testTodoistProjectNameNone(self):
        self.assertRaises(InvalidPreference, lambda: self.__setTodoistProjectNameToNone())

    def _backupPreferences(self):

        preferencesFileName: str = Preferences.getPreferencesLocation()
        source:              str = preferencesFileName
        target:              str = f"{preferencesFileName}{TestPreferences.BACKUP_SUFFIX}"
        if osPath.exists(source):
            try:
                copyfile(source, target)
            except IOError as e:
                self.logger.error(f'Unable to copy file. {e}')

    def _restoreBackup(self):

        preferencesFileName: str = Preferences.getPreferencesLocation()
        source: str = f"{preferencesFileName}{TestPreferences.BACKUP_SUFFIX}"
        target: str = preferencesFileName
        if osPath.exists(source):
            try:
                copyfile(source, target)
            except IOError as e:
                self.logger.error(f"Unable to copy file. {e}")

            osRemove(source)
        else:
            osRemove(target)

    def __setTodoistProjectNameToNone(self):
        preferences: Preferences = Preferences()
        preferences.todoistProjectName = cast(str, None)

    def __setTodoistProjectNameToEmpty(self):
        preferences: Preferences = Preferences()
        preferences.todoistProjectName = cast(str, None)


def suite() -> TestSuite:

    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestPreferences))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
