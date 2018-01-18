from requests import Session
from urllib.parse import urljoin, quote
import json

class ASnakeAuthError(Exception): pass

class ASnakeClient():
    '''ArchivesSnake Client'''

    def __init__(self, **config):
        self.__dict__.update(config)
        if not hasattr(self, 'session'): self.session = Session()
        self.session.headers.update({'Accept': 'application/json',
                                     'User-Agent': 'ArchivesSnake/0.1'})


    def authorize(self, username, password):
        resp = self.session.post(
            urljoin(self.baseurl, f'users/{quote(username)}/login'),
            params={"password": password, "expiring": False}
        )

        if resp.status_code != 200:
            raise ASnakeAuthError("Failed to authorize ASnake")
        else:
            self.session.headers['X-ArchivesSpace-Session'] = json.loads(resp.text)['session']
            return True

    def get(self, url, *args, **kwargs):
        return self.session.get(urljoin(self.baseurl, url), *args, **kwargs)
