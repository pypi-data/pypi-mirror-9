import os
from pscore.core.log import Log


class TestConfiguration():
    def __init__(self):
        pass

    @staticmethod
    def get_hub_url():
        return TestConfiguration.get_config_from_env('PSCORE_SELENIUM_HUB_URL', '')

    @staticmethod
    def get_amazon_hub_url():
        return TestConfiguration.get_config_from_env('PSCORE_AMAZON_HUB_URL', '')

    @staticmethod
    def get_sauce_username():
        return TestConfiguration.get_config_from_env('PSCORE_SAUCE_USERNAME', '')

    @staticmethod
    def get_sauce_key():
        return TestConfiguration.get_config_from_env('PSCORE_SAUCE_KEY', '')

    @staticmethod
    def get_sauce_parent_account():
        return TestConfiguration.get_config_from_env('PSCORE_SAUCE_PARENT_ACCOUNT', '')

    @staticmethod
    def get_sauce_tunnel_id():
        return TestConfiguration.get_config_from_env("PSCORE_SAUCE_TUNNEL_ID", 'tunnel_local')

    @staticmethod
    def get_execution_environment():
        return TestConfiguration.get_config_from_env('PSCORE_ENVIRONMENT', 'grid')

    @staticmethod
    def get_browser():
        return TestConfiguration.get_config_from_env('PSCORE_BROWSER', 'firefox')

    @staticmethod
    def get_browser_version():
        return TestConfiguration.get_config_from_env('PSCORE_BROWSER_VERSION', '')

    @staticmethod
    def get_homepage():
        return TestConfiguration.get_config_from_env('PSCORE_HOMEPAGE', '')

    @staticmethod
    def get_screenshot_dir():
        return TestConfiguration.get_config_from_env('PSCORE_SCREENSHOT_DIR', './')

    @staticmethod
    def get_config_from_env(env_key, default_value):
        env_value = os.getenv(env_key, 'Unspecified')
        if env_value == 'Unspecified':
            error_msg = "Environment variable '%s' not found. Defaulting to '%s'" % (env_key, default_value)
            Log.info(error_msg)
            return default_value
        return env_value