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

# Classes dealing with JSONModel imports
class JSONModelObject(metaclass=JSONModel):
    '''A wrapper over the JSONModel representation of a single object in ArchivesSpace.'''

    def __init__(self, json_rep, client = None):
        self.__json = json_rep
        self.__client = client or type(self).default_client()
        self.__is_ref = 'ref' in json_rep

    def reify(self):
        '''Convert object from a ref into a realized object.'''
        if self.__is_ref:
            self.__json = self.__client.get(self.__json['ref']).json()
            self.__is_ref = False
        return self

    def __dir__(self):
        self.reify()
        return sorted(chain(self.__json.keys(),
                    (x for x in self.__dict__.keys() if not x.startswith("_JSONModelObject__"))))

    def __repr__(self):
        result = "#<JSONModel:{}".format(self.__json['jsonmodel_type'] if not self.__is_ref else "ref" )

        if 'uri' in self.__json:
            result += ':' + self.uri
        elif self.__is_ref:
            result += ':' + self.__json['ref']
        return result + '>'

    def __getattr__(self, key):
        '''Access to properties on the JSONModel object and objects from  descendant API routes.

attr lookup for JSONModel object is provided from the following sources:

    - objects, lists of objects, and native values present in the wrapped JSON
    - API methods matching the object's URI + the attribute requested

If neither is present, the method raises an AttributeError.
'''
        self.reify()
        if not key.startswith('_'):
            if not key in self.__json.keys():
                uri = "/".join((self.__json['uri'].rstrip("/"), key,))
                if self.__client.head(uri, params={"all_ids":True}).status_code == 200:
                    return JSONModelRelation(uri, client=self.__client)
                else:
                    raise AttributeError("'{}' has no attribute '{}'".format(repr(self), key))

        if isinstance(self.__json[key], list):
            return [JSONModelObject(obj, self.__client) for obj in self.__json[key]]
        elif isinstance(self.__json[key], dict):
            return JSONModelObject(self.__json[key], self.__client)
        else:
            return self.__json[key]

    def __str__(self):
        return json.dumps(self.__json, indent=2)

    def __bytes__(self):
        return str(self).encode('utf8')

    def json(self):
        '''return wrapped dict representing JSONModelObject contents.'''
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

    def __call__(self, myid):
        '''Fetch a JSONModelObject from the relation by id.'''
        return JSONModelObject(self.client.get("/".join((self.uri.rstrip("/"), str(myid),))).json(), self.client)

    def __getattr__(self, key):
        return type(self)("/".join((self.uri, key,)), params=self.params, client=self.client)
