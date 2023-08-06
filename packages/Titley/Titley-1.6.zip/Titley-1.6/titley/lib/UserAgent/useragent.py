"""A module to further simplify using requests module"""

___version__ = "1.1"

from abc import ABCMeta, abstractmethod
import requests

def debug():
    """Enable advanced and verbose debugging at http client level"""
    import logging
    import http.client as http_client
    http_client.HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

class ProxyRotator(metaclass=ABCMeta):
    """Abstract base class for different proxy selection algorithms"""
    def __init__(self):
        self.proxies = {'http':[], 'https':[]}

    def add(self, protocol, proxy):
        """Add a proxy to for the protocol"""
        self.proxies[protocol].append(proxy)

    @abstractmethod
    def get(self, protocol):
        """Method that retrive a proxy according to the algoritm"""
        pass

class RoundRobinRotator(ProxyRotator):
    """Proxy selection using round robin algorithm"""
    def __init__(self):
        super().__init__()
        self.next_index = {'http':0, 'https':0}

    def get(self, protocol):
        if len(self.proxies[protocol]) == 0:
            return None
        next_index = self.next_index[protocol]
        proxy = self.proxies[protocol][next_index]
        if next_index == len(self.proxies[protocol]) - 1:
            self.next_index[protocol] = 0
        else:
            self.next_index[protocol] += 1
        return proxy

class UserAgent:
    """The public object"""
    def __init__(self, proxy_rotator=None):
        self.proxy_rotator = proxy_rotator
        self.session = None

    def start_session(self):
        """Start persisting cookies"""
        self.session = requests.Session()

    def end_session(self):
        """Stop persisting cookies"""
        self.session = None

    def get(self, url, **kargs):
        """Get response using GET method"""
        return self._get(url, 'get', **kargs)

    def head(self, url, **kargs):
        """Get response header using GET method"""
        return self._get(url, 'head', **kargs)

    def post(self, url, data):
        """Get response header using POST method,
           using POST data provided as a dictionary in 'data'"""
        return self._get(url, method='post', data=data)

    def _get(self, url, method='get', **kargs):
        """Implementation of get, post and head methods"""
        if self.proxy_rotator != None:
            proxies = self.proxy_rotator.get()
        else:
            proxies = None
        if self.session != None:
            req = self.session
        else:
            req = requests

        if method == 'get':
            response = req.get(url, proxies=proxies, **kargs)
        elif method == 'head':
            response = req.head(url, proxies=proxies, **kargs)
        elif method == 'post':
            response = req.post(url, proxies=proxies, **kargs)
        return response
