from requests import Session
from urllib.parse import quote
from numbers import Number
from collections.abc import Sequence, Mapping

import json
import asnake.configurator as conf
import asnake.logging as logging

log = None # initialized on first client init

class ASnakeError(Exception): pass
class ASnakeAuthError(ASnakeError): pass
class ASnakeWeirdReturnError(ASnakeError): pass
class ASnakeArgumentError(ASnakeError): pass

def listlike_seq(seq):
    '''Determine if a thing is a list-like (sequence of values) sequence that's not string-like.'''
    return isinstance(seq, Sequence) and not isinstance(seq, (str, bytes, Mapping,))

def http_meth_factory(meth):
    '''Utility method for producing HTTP proxy methods for ASnakeProxyMethods mixin class.

    Urls are prefixed with the value of baseurl from the client's ASnakeConfig.  Arguments are
    passed unaltered to the matching requests.Session method.'''
    def http_method(self, url, *args, **kwargs):
        # aspace uses the PHP convention where array-typed form values use names with '[]' appended
        if 'params' in kwargs:
            kwargs['params'] = {k + '[]' if listlike_seq(v) and k[-2:] != '[]' else k:v for k,v in kwargs['params'].items()}

        full_url = "/".join([self.config['baseurl'].rstrip("/"), url.lstrip("/")])
        result = getattr(self.session, meth)(full_url, *args, **kwargs)
        if result.status_code == 403 and self.config['retry_with_auth']:
            self.authorize()
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
        global log

        if 'config_file' in config:
            self.config = conf.ASnakeConfig(config['config_file'])
        else:
            self.config = conf.ASnakeConfig()

        self.config.update(config)

        # Only a subset of logging config can be supported in config
        # For more complex setups (configuring output format, say),
        # configure logs in Python code prior to loading
        #
        # Properties supported are:
        #    filename, filemode, level, and default_config
        # Default config can be any of the default configurations exposed in logging
        if not log:
            if not logging.already_configured and 'logging_config' in self.config:
                if 'default_config' in self.config['logging_config']:
                    default_logging_config = logging.configurations.get(
                        self.config['logging_config']['default_config'])
                    del self.config['logging_config']['default_config']
                else:
                    default_logging_config = None

                logging.setup_logging(config = default_logging_config,
                                      **self.config['logging_config'])

            log = logging.get_logger(__name__)

        if not hasattr(self, 'session'): self.session = Session()
        self.session.headers.update({'Accept': 'application/json',
                                     'User-Agent': 'ArchivesSnake/0.1'})
        log.debug("client created")


    def authorize(self, username=None, password=None, session_token=None, session_header_name=None):
        '''Authorizes the client against the configured archivesspace instance.

        Parses the JSON response, and stores the returned session token in the session.headers for future requests.
        Asks for a "non-expiring" session, which isn't truly immortal, just long-lived.'''

        # Populate values from config if empty
        username      = username or self.config.get('username', None)
        password      = password or self.config.get('password', None)
        session_token = session_token or self.config.get('session_token', None)

        if all((username, password, session_token,)):
            log.debug('argument error in authorize')
            raise ASnakeAuthError("Cannot set both username/password and session_token")

        session_header_name = session_header_name or self.config['session_header_name']

        # If we have a session_token already
        if session_token:
            self.session.headers[session_header_name] = session_token
            log.debug("setting session token directly")
            return session_token

        # Otherwise, use ASpace login to get one



        log.debug("authorizing against ArchivesSpace", user=username)

        resp = self.session.post(
            "/".join([self.config['baseurl'].rstrip("/"), 'users/{username}/login']).format(username=quote(username)),
            data={"password": password, "expiring": False}
        )

        if resp.status_code != 200:
            log.debug("authorization failure", status=resp.status_code)
            raise ASnakeAuthError("Failed to authorize ASnake with status: {}".format(resp.status_code))
        else:
            session_token = json.loads(resp.text)['session']
            self.session.headers[session_header_name] = session_token
            log.debug("authorization success", session_token=session_token)
            return session_token


    def get_paged(self, url, *args, page_size=100, **kwargs):
        '''get list of json objects from urls of paged items'''
        params = {}

        if "params" in kwargs:
            params.update(**kwargs['params'])
            del kwargs['params']

        # special-cased bc all_ids doesn't work on repositories index route
        if "all_ids" in params and url in {"/repositories", "repositories"}:
            del params['all_ids']

        params.update(page_size=page_size, page=1)

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
                        yield self.get("/".join([url, str(i)])).json()
                else:
                    raise ASnakeWeirdReturnError("get_paged doesn't know how to handle {}".format(current_json))
        else:
            raise ASnakeWeirdReturnError("get_paged doesn't know how to handle {}".format(current_json))
