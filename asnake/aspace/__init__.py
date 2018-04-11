from asnake.client import ASnakeClient
from asnake.jsonmodel import JSONModelObject, JSONModelRelation
from collections.abc import Sequence
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

    def __getattr__(self, attr):
        '''returns the JSONModelRelation representing the route with the same name as the attribute requested.'''
        if not attr.startswith('_'):
            return JSONModelRelation("/{}".format(attr), params={"all_ids": True}, client = self.__client)

    @property
    def resources(self):
        '''return all resources from every repo.'''

        repo_uris = [r['uri'] for r in self.__client.get('repositories').json()]
        for resource in chain(*[self.__client.get_paged('{}/resources'.format(uri)) for uri in repo_uris]):
            yield JSONModelObject(resource, self.__client)

    @property
    def agents(self):
        '''returns an AgentRelation.'''
        return AgentRelation("/agents", {}, self.__client)

class ASNakeBadAgentType(Exception): pass

agent_types = ("corporate_entities", "people", "families", "software",)
agent_types_set = frozenset(agent_types)
class AgentRelation(JSONModelRelation):
    '''subtype of JSONModelRelation for handling the `/agents` route hierarchy.

Usage:

.. code-block:: python

    ASpace().agents                        # all agents of all types
    ASpace().agents.corporate_entities     # JSONModelRelation of corporate entities
    ASpace().agents["corporate_entities"]  # see above
    ASpace().agents["people", "families"]  # Multiple types of agents

'''

    def __iter__(self):
        for agent_type in agent_types:
            yield from JSONModelRelation("/".join((self.uri.rstrip("/"), agent_type,)),
                                         {"all_ids": True},
                                         self.client)

    def __getitem__(self, only):
        '''filter the AgentRelation to only the type or types passed in'''
        if isinstance(only, str):
            if not only in agent_types_set:
                raise ASnakeBadAgentType("'{}' is not a type of agent ASnake knows about".format(only))
            return JSONModelRelation("/".join((self.uri.rstrip("/"), only,)),
                                         {"all_ids": True},
                                         self.client)
        elif isinstance(only, Sequence) and set(only) < agent_types_set:
            return chain(*(JSONModelRelation("/".join((self.uri.rstrip("/"), agent_type,)),
                                             {"all_ids": True},
                                             self.client) for agent_type in only))
        else:
            raise ASnakeBadAgentType("'{}' is not a type resolvable to an agent type or set of agent types".format(only))

    def __repr__(self):
        return "#<AgentRelation:/agents>"

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("__call__ is not implemented on AgentRelation")
