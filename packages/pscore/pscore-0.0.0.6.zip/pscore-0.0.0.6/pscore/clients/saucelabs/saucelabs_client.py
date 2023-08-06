from pscore.clients.saucelabs.sauceclient import SauceClient


class SauceLabsClient(SauceClient):
    def __init__(self, sauce_username=None, sauce_access_key=None):
        SauceClient.__init__(self, sauce_username, sauce_access_key)

    def job_is_complete(self, job_id):
        """Ascertain if the specified job is complete. """
        end_time = self.jobs.get_job_attributes(job_id)["end_time"]
        job_is_complete = end_time != '0'

        return job_is_complete

    def set_job_public(self, job_id, is_public):
        """Set the specified job public so authentication is not required to view it."""
        self.jobs.update_job(job_id, public=is_public)

    def set_job_pass_status(self, job_id, is_passed):
        """Set the pass status of the specified job."""
        self.jobs.update_job(job_id, passed=is_passed)

    def set_error(self, job_id, error):
        """Set an error message for the specified job."""
        if self.jobs.get_job_attributes(job_id)["error"] == '':
            cerror = {'custom-data': {'customerror': error}}
            self.jobs.update_job(job_id=job_id, build_num=None,
                                 custom_data=cerror,
                                 name=None, passed=None, public=None, tags=None)