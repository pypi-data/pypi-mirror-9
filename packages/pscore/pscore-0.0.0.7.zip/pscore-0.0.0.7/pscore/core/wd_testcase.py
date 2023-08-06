import sys
from unittest import TestCase

from pscore.core.factories import WebDriverFactory
from pscore.core.finalizers import WebDriverFinalizer
from pscore.core.log import Log

"""
This module includes any required TestCase subclasses.  These are then subclassed by the consuming test classes
to inherit the setup and teardown hooks responsible for initiating driver instanstiation, finalization and any resulting
actions.
"""


class WebDriverTestCase(TestCase):
    """
    This is the default (and currently only!) option for hooking.

    Example:
        class TestFlightsSearch(WebDriverTestCase):
    """
    failureExceptions = AssertionError
    failureInfo = None

    def setUp(self):
        """
        The setup hook.  This will be called before each individual test.
        """
        # TODO: Consider deleting existing screenshots here - this would make the dir specifically relevant to the run and makes skygrid integ easier
        self.driver = WebDriverFactory.get(self._testMethodName)

    def tearDown(self):
        """
        The teardown hook.  This will be called after each individual test.
        """
        Log.info("Test Runner: Attempting to teardown.")
        WebDriverFinalizer.finalize(self.driver, self.has_failed())

    def has_failed(self):
        """
        This method encapsulates (and illustrates how to) ascertain a test failure state.
        """
        return self.failureInfo is not None

    def run(self, result=None):
        """
        This is the over-ridden version of run(), to allow us to track if a test has failed.
        This allows us to then differentiate between passed and failed results in teardown.
        It should be agnostic to the execution environment, so equally applicable to local tests,
        grid tests, saucelabs tests, etc.
        """
        success = False
        orig_result = result

        try:
            testMethod = getattr(self, self._testMethodName)

            Log.info("Test Runner: Running test setup: {0}".format(str(self)))
            self.setUp()

            try:
                Log.info("Test Runner: Running test: {0}".format(str(self)))
                testMethod()

            except:
                Log.info("Test Runner: Adding failure to result for {0}".format(str(self)))
                result.addFailure(self, sys.exc_info())
                Log.info("Test Runner: Recording failure info for teardown for {0}".format(str(self)))
                self.failureInfo = sys.exc_info()

            else:
                success = True

            try:
                Log.info("Test Runner: Tearing down test: {0}".format(str(self)))
                self.tearDown()
            except KeyboardInterrupt:
                raise

            cleanUpSuccess = self.doCleanups()
            success = success and cleanUpSuccess
            if success:
                result.addSuccess(self)

        except Exception as e:
            Log.error("OMG! See - https://external.skyscanner.co.uk/jira/browse/TAS-296 {} {}".format(type(e), e.message))

        finally:
            result.stopTest(self)
            if orig_result is None:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()