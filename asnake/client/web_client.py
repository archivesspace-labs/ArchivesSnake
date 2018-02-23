from requests import Session
from urllib.parse import urljoin, quote
import json
import asnake.configurator as conf
import asnake.logging as logging

log = logging.get_logger(__name__)

class ASnakeAuthError(Exception): pass

def http_meth_factory(meth):
    '''Utility method for producing HTTP proxy methods for ASnakeProxyMethods mixin class.

    Urls are prefixed with the baseurl defined  All arguments are p
    '''
    def http_method(self, url, *args, **kwargs):
        full_url = urljoin(self.config['baseurl'], url)
        result = getattr(self.session, meth)(full_url, *args, **kwargs)
        log.debug("proxied http method", method=meth.upper(), url=full_url, status=result.status_code)
        return result
    return http_method


class ASnakeProxyMethods(type):
    '''Metaclass to set up proxy methods for all requests-supported HTTP methods'''
    def __init__(cls, name, parents, dct):

        for meth in ('get', 'post', 'head', 'put', 'delete', 'options',):
            fn = http_meth_factory(meth)
            fn.__name__ = meth
            fn.__doc__ = '''Proxied :meth:`requests.Session.{}` method from :class:`requests.Session`'''.format(meth)

            setattr(cls, meth, fn)

class ASnakeClient(metaclass=ASnakeProxyMethods):
    '''ArchivesSnake Web Client'''

    def __init__(self, **config):
        self.config = conf.ASnakeConfig()
        self.config.update(config)

        if not hasattr(self, 'session'): self.session = Session()
        self.session.headers.update({'Accept': 'application/json',
                                     'User-Agent': 'ArchivesSnake/0.1'})
        log.debug("client created")


    def authorize(self, username=None, password=None):
        '''Authorizes the client against the configured archivesspace instance.

        Parses the JSON response, and stores the returned session token in the session.headers for future requests.
        Asks for a "non-expiring" session, which isn't truly immortal, just long-lived.'''

        username = username or self.config['username']
        password = password or self.config['password']

        log.debug("authorizing against ArchivesSpace", user=username)

        resp = self.session.post(
            urljoin(self.config['baseurl'], 'users/{username}/login'.format(username=quote(username))),
            params={"password": password, "expiring": False}
        )

        if resp.status_code != 200:
            log.debug("authorization failure", status=resp.status_code)
            raise ASnakeAuthError("Failed to authorize ASnake with status: {}".format(resp.status_code))
        else:
            session_token = json.loads(resp.text)['session']
            self.session.headers['X-ArchivesSpace-Session'] = session_token
            log.debug("authorization success", session_token=session_token)
            return session_token
