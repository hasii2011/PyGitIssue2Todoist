
from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from tests.TestBase import TestBase

# import the class you want to test here
# from org.pyut.template import template


class TestTemplate(TestBase):
    """
    You need to change the name of this class to Test`xxxx`
    Where `xxxx' is the name of the class that you want to test.

    See existing tests for more information.
    """
    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestTemplate.clsLogger = getLogger(__name__)

    def setUp(self):
        self.logger: Logger = TestTemplate.clsLogger

    def tearDown(self):
        pass

    def testName1(self):
        pass

    def testName2(self):
        """Another test"""
        pass


def suite() -> TestSuite:
    """You need to change the name of the test class here also."""
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestTemplate))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
