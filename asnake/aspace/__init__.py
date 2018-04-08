from asnake.client import ASnakeClient
from asnake.jsonmodel import JSONModelObject, JSONModelRelation
from itertools import chain
import json
import re

class ASpace():

        # this happens when you call ASpace()
        def __init__(self, **config):
                # Connect to ASpace using .archivessnake.yml
                self.__client = ASnakeClient(**config)
                self.__client.authorize()
                m = re.match(r'\(v?(.+\))', self.__client.get('version').text)
                if m:
                        self.version = m[1]
                else:
                        self.version = 'unknown version'

        # this automatically sets attributes to ASpace(), so you can ASpace().resources, etc.
        def __getattr__(self, attr):
                if not attr.startswith('_'):
                        return JSONModelRelation("/{}".format(attr), params={"all_ids": True}, client = self.__client)

        @property
        def resources(self):
                '''return all resources from every repo'''

                repo_uris = [r['uri'] for r in self.__client.get('repositories').json()]
                for resource in chain(*[self.__client.get_paged('{}/resources'.format(uri)) for uri in repo_uris]):
                        yield JSONModelObject(resource, self.__client)

