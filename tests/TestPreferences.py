
from typing import cast

from logging import Logger
from logging import getLogger

from os import path as osPath
from os import remove as osRemove

from shutil import copyfile

from unittest import TestSuite
from unittest import main as unitTestMain

from gittodoistclone.general.exceptions.InvalidPreference import InvalidPreference

from gittodoistclone.general.Preferences import Preferences

from tests.TestBase import TestBase


class TestPreferences(TestBase):
    """
    """
    BACKUP_SUFFIX: str = '.backup'

    clsLogger: Logger = cast(Logger, None)

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestPreferences.clsLogger = getLogger(__name__)
        Preferences.determinePreferencesLocation()          # Must do this once

    def setUp(self):

        self.logger: Logger = TestPreferences.clsLogger
        self._backupPreferences()

    def tearDown(self):
        self._restoreBackup()

    def testNoPreferencesExist(self):

        preferences: Preferences = Preferences()
        self.assertIsNotNone(preferences, 'Ouch.  Was not created')

    def testTodoistApiToken(self):

        preferences: Preferences = Preferences()

        preferences.todoistApiToken = '77777'

        self.assertEqual('77777', preferences.todoistApiToken, 'Uh oh, token did not change')

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
        preferences.todoistProjectName = None

    def __setTodoistProjectNameToEmpty(self):
        preferences: Preferences = Preferences()
        preferences.todoistProjectName = None


def suite() -> TestSuite:

    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestPreferences))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
