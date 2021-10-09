
from typing import List

from logging import Logger
from logging import getLogger

from sys import path as sysPath
from sys import argv as sysArgv

from importlib import import_module

from glob import glob

from unittest import TestResult
from unittest import TextTestRunner
from unittest.suite import TestSuite

from HtmlTestRunner import HTMLTestRunner


class TestAll:
    """
    The class that can run our unit tests in various formats
    """
    NOT_TESTS: List[str] = ['TestAll', 'TestTemplate', 'TestBase', 'TestTodoistAdapterBase', 'TestTodoistAdapterReal', 'TestADialog']

    VERBOSITY_QUIET:   int = 0  # Print the total numbers of tests executed and the global result
    VERBOSITY_DEFAULT: int = 1  # VERBOSITY_QUIET plus a dot for every successful test or a F for every failure
    VERBOSITY_VERBOSE: int = 2  # Print help string of every test and the result
    VERBOSITY_LOUD:    int = 3  # ??

    def __init__(self):

        self._setupSystemLogging()

        self.logger: Logger = getLogger(__name__)

        self._testSuite: TestSuite = self._getTestSuite()

    def runTextTestRunner(self) -> int:

        status: TestResult = TextTestRunner(verbosity=TestAll.VERBOSITY_QUIET).run(self._testSuite)
        self.logger.info(f'Test Suite Status: {status}')
        if len(status.failures) != 0:
            return 1
        else:
            return 0

    def runHtmlTestRunner(self) -> int:

        runner = HTMLTestRunner(report_name='PyUtTestResults', combine_reports=True, add_timestamp=True)
        status = runner.run(self._testSuite)
        if len(status.failures) != 0:
            return 1
        else:
            return 0

    def _setupSystemLogging(self):
        """
        Read the unit test logging configuration file
        """
        from tests.TestBase import TestBase

        TestBase.setUpLogging()

    def _getTestSuite(self) -> TestSuite:
        """

        Returns:
            A suite of all tests in the unit test directory
        """
        modules: List[str] = self.__getTestableModuleNames()
        fSuite: TestSuite = TestSuite()
        for module in modules:
            try:
                fixedName: str = module.replace('/', '.')
                m = import_module(fixedName)
                # noinspection PyUnresolvedReferences
                fSuite.addTest(m.suite())   # type: ignore
            except (ValueError, Exception) as e:
                self.logger.error(f'Module import problem with: {module}:  {e}')
        return fSuite

    def __getTestableModuleNames(self) -> List[str]:
        """
        Removes modules that are not unit tests

        Returns:
            A list of module names that we can find in this package
        """

        fModules = glob("tests/Test*.py")
        # remove .py extension
        modules = list(map(lambda x: x[:-3], fModules))
        for doNotTest in TestAll.NOT_TESTS:
            modules.remove(f'tests/{doNotTest}')

        return modules


def main():

    if ".." not in sysPath:
        sysPath.append("..")  # access to the classes to test

    testAll: TestAll = TestAll()
    status: int = 0
    if len(sysArgv) < 2:
        status: int = testAll.runTextTestRunner()
    else:
        for param in sysArgv[1:]:
            if param[:22] == "--produce-html-results":
                print(f'Running HTML Tests')
                status: int = testAll.runHtmlTestRunner()

    return status


if __name__ == "__main__":
    cliStatus: int = main()
    exit(cliStatus)
