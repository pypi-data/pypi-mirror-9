from datetime import datetime, time
import logging
import uuid
from pscore.clients.saucelabs.saucelabs_client import SauceLabsClient
from pscore.config.test_configuration import TestConfiguration
from pscore.core.log import Log


class WebDriverFinalizer:
    # TODO: Move to config
    SCREENSHOT_PATH = './tmp/screenshots/'

    @staticmethod
    def create_screenshot_filename():
        return str(uuid.uuid4()) + '.png'

    @staticmethod
    def finalize(driver, test_failed):
        """
        :type driver: selenium.webdriver.remote.webdriver.WebDriver
        """

        desired_execution_environment = TestConfiguration.get_execution_environment()

        if desired_execution_environment == 'grid':
            WebDriverFinalizer.finalise_grid_driver(driver, test_failed)

            return

        elif desired_execution_environment == 'local':
            WebDriverFinalizer.finalise_grid_driver(driver, test_failed)
            return

        elif desired_execution_environment == 'skygrid':
            WebDriverFinalizer.finalise_skygrid_driver(driver, test_failed)
            return

        elif desired_execution_environment in ['saucelabs', 'sauce']:
            WebDriverFinalizer.finalise_saucelabs_driver(driver, test_failed)
            return

        else:
            Log.error(
                "Could not teardown driver properly as the specified execution environment was not recognised: %s "
                % desired_execution_environment)

        # Catch-all driver teardown.  This shouldn't be needed, but just in case something crazy happens we don't want
        # to leave any orphaned sessions open
        if driver is not None:
            Log.info(
                "Could not parse driver to finalize in any specific fashion.  Quitting driver to prevent orphan session.")
            driver.quit()

        return

    @staticmethod
    def finalise_saucelabs_driver(driver, test_failed):
        Log.info("Finalizing driver for Saucelabs")
        try:
            job_id = driver.session_id
            Log.debug("Quitting driver instance.")
            driver.quit()

            Log.debug("Creating Saucelabs client.")
            client = SauceLabsClient(sauce_username=TestConfiguration.get_sauce_username(),
                                     sauce_access_key=TestConfiguration.get_sauce_key())

            Log.debug("Waiting for job to complete.")
            WebDriverFinalizer.wait_until_sauce_job_completes(client, job_id)

            Log.debug("Setting job public.")
            client.set_job_public(job_id, True)

            if test_failed:
                Log.debug("Setting job pass status to False.")
                client.set_job_pass_status(job_id, False)
                # TODO: May want to pull error information from test here to output to log - that may have to be explicitly stored in state
                error = 'example error text'
                Log.debug("Setting job error text.")
                client.set_error(job_id, error)
                Log.info('SauceLabs report: https://saucelabs.com/jobs/' + str(job_id))

            else:
                Log.debug("Setting job pass status to True.")
                client.set_job_pass_status(job_id, True)
                Log.info('SauceLabs report: https://saucelabs.com/jobs/' + str(job_id))
        except TypeError as e:
            Log.error(
                "TypeError caught when finalizing for SauceLabs.  This signifies a problem in the finalization code: %s" % str(
                    e))
            raise

        except Exception as e:
            Log.error("Exception caught when finalizing for SauceLabs: %s" % str(e))
            raise

    @staticmethod
    def wait_until_sauce_job_completes(client, job_id):
        polling_delay_sec = 1
        max_attempts = 10
        job_completed = False

        for x in range(1, max_attempts):
            job_completed = client.job_is_complete(job_id)
            if job_completed:
                break
            else:
                time().sleep(polling_delay_sec)

        if not job_completed:
            Log.error("Saucelabs job %s did not complete within %s seconds during finalization"
                      % (job_id, str(max_attempts * polling_delay_sec)))

    # noinspection PyUnreachableCode
    @staticmethod
    def finalise_skygrid_driver(driver, test_failed):
        raise RuntimeError("SkyGrid finalisation not implemented yet.")

        try:
            if driver is not None:
                if test_failed:

                    metadata_client = SkyGridMetaDataClient()
                    screenshot_path = metadata_client.take_screenshot()
                    test_session_id = metadata_client.session_id()

                    # There's another option here - we could just collect all available screenshots, assuming
                    # that the startup hook has cleared all available
                    to_add_to_global_list_of_screenshots(screenshot_path)

                    test_name = get_test_name()
                    error_message = get_error_message()
                    timestamp = datetime.now()
                    duration = get_test_start_time_from_global_state_and_subtract_timestamp()
                    node_ip = get_node_ip()
                    node_hostname = node_ip
                    browser_name = get_browser_name()
                    browser_version = get_browser_version()
                    operating_system = get_operating_system()
                    user_descriptor = 'pysel harness'

                    # construct test details object from above

                    metadata_client.upload_video()
                    metadata_client.upload_screenshots(get_global_list_of_screenshots())
                    metadata_client.upload_test_details(test_details)
                    metadata_client.upload_log(get_test_log())

                    Log.info('SkyGrid Test Report: ' + metadata_client.get_test_report_uri())
                    Log.info('SkyGrid Test Run Report: ' + metadata_client.get_test_run_report_uri())

                    del metadata_client
                    pass
                else:
                    Log.info('Test Finalizer: Detected test passed.')

                Log.info('Test Finalizer: Ending browser session.')

            else:
                logging.warning('Test Finalizer: Attempted to finalise test but the session had already terminated.')

        finally:
            if driver is not None:
                driver.quit()
        pass

    @staticmethod
    def finalise_grid_driver(driver, test_failed):
        if driver is not None:
            if test_failed:
                filename = WebDriverFinalizer.create_screenshot_filename()
                Log.info('Test Finalizer: Detected test failure, attempting screenshot: ' + filename)

                try:
                    driver.save_screenshot(WebDriverFinalizer.SCREENSHOT_PATH + filename)
                except:
                    Log.error('Test Finalizer: Exception thrown when attempting screenshot: ' + filename)

                try:
                    final_url = driver.current_url
                    Log.info('Test Finalizer: Final url: ' + final_url)
                except:
                    Log.error('Test Finalizer: Exception thrown when attempting to get the drivers final url')

            else:
                Log.info('Test Finalizer: Detected test passed.')

            Log.info('Test Finalizer: Ending browser session.')
            driver.quit()

        else:
            logging.warning('Test Finalizer: Attempted to finalise test but the session had already terminated.')
