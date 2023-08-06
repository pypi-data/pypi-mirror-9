from selenium.webdriver.remote.webdriver import WebDriver
# Example driver extension

class SkyGridDriver(WebDriver):
    def __init__(self, command_executor='http://127.0.0.1:4444/wd/hub', desired_capabilities=None, browser_profile=None,
                 proxy=None, keep_alive=False):
        WebDriver.__init__(self, command_executor, desired_capabilities, browser_profile, proxy, keep_alive)

    pass