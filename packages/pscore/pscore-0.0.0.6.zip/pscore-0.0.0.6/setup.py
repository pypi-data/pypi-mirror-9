from setuptools import setup, find_packages

setup(
    name='pscore',
    packages=find_packages(),  # this must be the same as the name above
    version='0.0.0.6',
    description='Prototype Python-Selenium framework module',
    author='Andrew Fowler',
    author_email='andrew.fowler@skyscanner.net',
    url='http://nope.com',  # use the URL to the github repo
    download_url='http://nope.com',  # I'll explain this in a second
    keywords=['selenium', 'webdriver', 'saucelabs', 'grid'],  # arbitrary keywords
    classifiers=[], requires=['selenium'], install_requires=['selenium==2.44.0', 'requests==2.5.1']
)