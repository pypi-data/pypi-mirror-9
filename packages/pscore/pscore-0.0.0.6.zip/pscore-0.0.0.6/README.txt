PLEASE NOTE: Required environment variables

### Required environment variables

* PSCORE_ENVIRONMENT - Specifies the execution environment.  Accepted values: grid, local, saucelabs, amazon
* PSCORE_BROWSER - Specifies the browser.  Accepted values: chrome, firefox, ie
* PSCORE_HOMEPAGE - Specifies the homepage.  E.g. http://www.skyscanner.net

### Other variables

* PSCORE_SCREENSHOT_DIR - Specifies the directory to write screenshots to. E.g. ./tmp/screenshot
* PSCORE_SELENIUM_HUB_URL - Specifies the URL of a standard selenium hub instance
* PSCORE_AMAZON_HUB_URL - Specifies the URL of an amazon hosted selenium hub instance
* PSCORE_SAUCE_USERNAME - The username to use for Saucelabs authentication
* PSCORE_SAUCE_KEY - The access key to use for Saucelabs authentication
* PSCORE_SAUCE_TUNNEL_ID
* PSCORE_SAUCE_PARENT_ACCOUNT