

from unittest import TestSuite
from unittest import TestCase
from unittest import main as unitTestMain

from pygitissue2todoist.general.Singleton import Singleton


class Child(Singleton):
    """
    Good Test class.
    """
    def init(self, val):
        self.val = val


class BadChild(Singleton):
    """
    Bad test class.
    """
    def __init__(self, val):
        self.val = val


class TestSingleton(TestCase):
    """
    """
    def testSingleton(self):
        """Test instances of Singleton"""
        a = Singleton()
        b = Singleton()
        self.assertTrue(a is b, "Error, two singletons are not the same.")

    def testSingletonChild(self):
        """Test instances of classes derived from Singleton"""
        a = Child(10)
        b = Child(11)
        self.assertTrue(a is b, "Error, two singletons are not the same.")

    def testBadSingletonClass(self):
        """Test bad derivations of Singleton"""
        try:
            a = BadChild(10)
        except AssertionError:
            pass  # OK
        else:
            self.fail("This should have raised an AssertionError")

    def testFailedInitialization(self):
        """Test failed initialization of a singleton"""
        try:
            a = Child()
        except TypeError:
            pass  # normal behaviour
        a = Child(10)  # good initialization
        self.assertTrue(a.val == 10, "Not correctly initialized")
        a = Child()  # now this works, because the singleton is already instantiated


def suite() -> TestSuite:

    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestSingleton))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
