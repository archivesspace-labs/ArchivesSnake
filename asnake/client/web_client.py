from requests import Session
from urllib.parse import urljoin, quote
from numbers import Number

import json
import asnake.configurator as conf
import asnake.logging as logging

log = logging.get_logger(__name__)

class ASnakeAuthError(Exception): pass
class ASnakeWeirdReturnError(Exception): pass

def http_meth_factory(meth):
    '''Utility method for producing HTTP proxy methods for ASnakeProxyMethods mixin class.

    Urls are prefixed with the value of baseurl from the client's ASnakeConfig.  Arguments are
    passed unaltered to the matching requests.Session method.'''
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


    def get_paged(self, url, *args, page_size=10, **kwargs):
        '''get list of json objects from urls of paged items'''
        params = {"page_size": page_size, "page": 1}
        if "params" in kwargs:
            params.update(**kwargs['params'])
            del kwargs['params']

        current_page = self.get(url, params=params, **kwargs)
        current_json = current_page.json()
        # Regular paged object
        if hasattr(current_json, 'keys') and \
           {'results', 'this_page', 'last_page'} <= set(current_json.keys()):
            while current_json['this_page'] <= current_json['last_page']:
                for obj in current_json['results']:
                    yield obj
                if current_json['this_page'] == current_json['last_page']: break
                params['page'] += 1
                current_page = self.get(url, params=params)
                current_json = current_page.json()
        # routes that just return a list,  or ids, i.e. queries with all_ids param
        elif isinstance(current_json, list):
            # e.g. repositories
            if len(current_json) >= 1:
                if hasattr(current_json[0], 'keys'):
                    for obj in current_json:
                        yield obj
                elif isinstance(current_json[0], Number):
                    for i in current_json:
                        yield self.get(urljoin(url, str(i))).json()
                else:
                    raise ASnakeWeirdReturnError("get_paged doesn't know how to handle {}".format(current_json))
        else:
            raise ASnakeWeirdReturnError("get_paged doesn't know how to handle {}".format(current_json))
