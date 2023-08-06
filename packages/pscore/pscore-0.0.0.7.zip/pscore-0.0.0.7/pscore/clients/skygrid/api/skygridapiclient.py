# noinspection PyUnresolvedReferences
# from SkyGrid.metadata.SkyGridMetaDataClient import SkyGridMetaDataClient
from pscore.clients.skygrid.metadata.skygridmetadataclient import SkyGridMetaDataClient


class SkyGridApiClient():
    def __init__(self, driver, hub_url, metadata_service_url):

        self.hub_url = hub_url
        self.metadata_service_url = metadata_service_url
        self.metadata_client = SkyGridMetaDataClient(metadata_service_url)

        self.session_id = driver.session_id
        self.node_ip = driver.get_active_node_ip(hub_url, self.session_id)
        self.video_output_directory = self.get_video_output_directory(self.node_ip)

        pass

    def take_screenshot(self):
        pass

    def session_id(self):
        pass

    def upload_video(self):
        pass

    def upload_screenshots(self):
        pass

    def upload_test_details(self):
        pass

    def upload_log(self):
        pass

    def get_test_report_uri(self):
        pass

    def get_test_run_report_uri(self):
        pass

    def get_video_output_directory(self, node_ip):
        # create rest client
        # create request
        # get config runtime response data
        # get video output dir from config runtime response data
        # return video output dir
        return ''