"""A module that implements a bot that returns beautifulsoup objects"""

__version__ = "1.1"

from bs4 import BeautifulSoup
from ..UserAgent.useragent import UserAgent

class Bot:
    """A bot that implements additional logic over a user agent object
    which are,
    1.Persists cookies
    2.Ability to set base url for easing specifying of relative urls
    3.Return response object or parsed beautifulsoup trees
    4.Download and save a file from a url"""

    def __init__(self):
        self.user_agent = UserAgent()
        self.user_agent.start_session()
        self.base_url = ''
        self.options = {}

    def set_base_url(self, url):
        """Set a url that will be prepended to all relative urls"""
        self.base_url = url

    def download_file(self, url, filename):
        """Download a file from the 'url' and save as 'filename'"""
        resp = self.user_agent.get(url, stream=True)
        with open(filename, 'wb') as flh:
            for chunk in resp.iter_content(chunk_size=1204):
                flh.write(chunk)
                flh.flush()

    def get(self, url, **kargs):
        """Retrive content at url as response object(requst's)"""
        if url[0] == '/':
            url = self.base_url + url
        kargs.update(self.options)
        resp = self.user_agent.get(url, **kargs)
        return resp

    def get_parsed_content(self, url, **kargs):
        """Retrive content at url as a parsed bs4 object"""
        resp = self.get(url, **kargs)
        return get_soup(resp.text)

def get_soup(text):
    """Make bs4 object from html text"""
    soup = BeautifulSoup(text, "html5lib")
    soup = BeautifulSoup(soup.prettify(), "html5lib")
    return soup
