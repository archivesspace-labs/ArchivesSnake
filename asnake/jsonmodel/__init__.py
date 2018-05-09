from itertools import chain

# Base metaclass for shared functionality
class JSONModel(type):
    '''Mixin providing functionality shared by JSONModel and JSONModelRelation classes.'''

    def __init__(cls, name, parents, dct):
        cls.__default_client = None

    def default_client(cls):
        '''return existing ASnakeClient or create, store, and return a new ASnakeClient'''
        if not cls.__default_client:
            from asnake.client import ASnakeClient
            cls.__default_client = ASnakeClient()
        return cls.__default_client

jmtype_signifiers = frozenset({"ref", "jsonmodel_type"})
def is_jmtype(obj):
    '''Determines if object is JSON suitable for wrapping with a JSONModelObject.'''
    return isinstance(obj, dict) and jmtype_signifiers.intersection(jmtype_signifiers)

# Classes dealing with JSONModel imports
class JSONModelObject(metaclass=JSONModel):
    '''A wrapper over the JSONModel representation of a single object in ArchivesSpace.'''

    def __init__(self, json_rep, client = None):
        self.__json = json_rep
        self.__client = client or type(self).default_client()
        self.is_ref = 'ref' in json_rep

    def reify(self):
        '''Convert object from a ref into a realized object.'''
        if self.is_ref:
            if '_resolved' in self.__json:
                self.__json = self.__json['_resolved']
            else:
                self.__json = self.__client.get(self.__json['ref']).json()
            self.is_ref = False
        return self

    @property
    def id(self):
        '''Return the id for the object if it has a useful ID, or else None.

Note: unlike uri, an id is Not fully unique within some collections returnable
by API methods.  For example, searches can return different types of objects, and
agents have unique ids per agent_type, not across all agents.'''
        candidate = self.__json.get('uri', self.__json.get('ref', None))
        if candidate:
            val = candidate.split('/')[-1]
            if val.isdigit(): return(int(val))

    def __dir__(self):
        self.reify()
        return sorted(chain(self.__json.keys(),
                    (x for x in self.__dict__.keys() if not x.startswith("_JSONModelObject__"))))

    def __repr__(self):
        result = "#<JSONModel:{}".format(self.__json['jsonmodel_type'] if not self.is_ref else "ref" )

        if 'uri' in self.__json:
            result += ':' + self.__json['uri']
        elif self.is_ref:
            result += ':' + self.__json['ref']
        return result + '>'


    def __getattr__(self, key):
        '''Access to properties on the JSONModel object and objects from  descendant API routes.

attr lookup for JSONModel object is provided from the following sources:

    - objects, lists of objects, and native values present in the wrapped JSON
    - API methods matching the object's URI + the attribute requested

If neither is present, the method raises an AttributeError.'''
        if self.is_ref:
            if key == 'uri': return self.__json['ref']
            self.reify()

        if not key.startswith('_') and not key == 'is_ref':
            if not key in self.__json.keys() and 'uri' in self.__json:
                uri = "/".join((self.__json['uri'].rstrip("/"), key,))
                # Existence of route isn't enough, need to discriminate by type
                # example: .../resources/:id/ordered_records which ALSO ought to be maybe treated as plural?
                # This works, at the cost of a "wasted" full call if not a JSONModelObject
                resp = self.__client.get(uri, params={"all_ids":True})
                if resp.status_code == 200:
                    if is_jmtype(resp.json()):
                        return JSONModelObject(resp.json(), client=self.__client)
                    return JSONModelRelation(uri, client=self.__client)
                else:
                    raise AttributeError("'{}' has no attribute '{}'".format(repr(self), key))

            if isinstance(self.__json[key], list):
                if len(self.__json[key]) == 0 or is_jmtype(self.__json[key][0]):
                    return [JSONModelObject(obj, self.__client) for obj in self.__json[key]]
                else:
                    # bare lists of Not Jsonmodel Stuff, ding dang note contents and suchlike
                    return self.__json[key]
            elif is_jmtype(self.__json[key]):
                return JSONModelObject(self.__json[key], self.__client)
            else:
                return self.__json[key]
        else: return self.__getattribute__(key)

    def __str__(self):
        return json.dumps(self.__json, indent=2)

    def __bytes__(self):
        return str(self).encode('utf8')

    def json(self):
        '''return wrapped dict representing JSONModelObject contents.'''
        self.reify()
        return self.__json

class JSONModelRelation(metaclass=JSONModel):
    '''A wrapper over index routes and other routes that represent groups of items in ASpace.

It provides two means of accessing objects in these collections:

    - you can iterate over the relation to get all objects
    - you can call the relation as a function with an id to get an object with a known id

e.g.

.. code-block:: python

    for repo in ASpace().repositories:
        # do stuff with repo here

    ASpace.repositories(12) # object at uri /repositories/12

This object wraps the route and parameters, and does no caching - each iteration through a relation fetches data from ASpace fresh.

Additionally, JSONModelRelations implement `__getattr__`, in order to handle nested and subsidiary routes, such as the routes for individual types of agents.'''

    def __init__(self, uri, params = {}, client = None):
        self.uri = uri
        self.client = client or type(self).default_client()
        self.params = params

    def __repr__(self):
        return "#<JSONModelRelation:{}:{}>".format(self.uri, self.params)

    def __iter__(self):
        for jm in self.client.get_paged(self.uri, params=self.params):
            yield JSONModelObject(jm, self.client)

    def __call__(self, myid, **params):
        '''Fetch a JSONModelObject from the relation by id.'''
        # Special handling for resolve because it takes a string or an array and requires [] for array
        if 'resolve' in params:
            params['resolve[]'] = params['resolve']
            del params['resolve']
        return JSONModelObject(self.client.get("/".join((self.uri.rstrip("/"), str(myid),)), params=params).json(), self.client)

    def with_params(self, **params):
        '''Return JSONModelRelation with same uri and client, but add kwargs to params.'''
        return JSONModelRelation(self.uri, {**self.params, **params}, self.client)

    def __getattr__(self, key):
        return type(self)("/".join((self.uri, key,)), params=self.params, client=self.client)


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

    # override parent __getattr__ because needs to return base class impl for descendant urls
    def __getattr__(self, key):
        return type(self).__bases__[0]("/".join((self.uri, key,)), params=self.params, client=self.client)
