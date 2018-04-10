from itertools import chain
import json

# Base metaclass for shared functionality
class JSONModel(type):
        def __init__(cls, name, parents, dct):
                cls.__default_client = None

        def default_client(cls):
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
                '''Access to properties on the JSONModel object. '''
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

        # utility methods
        def pp(self):
                print (json.dumps(self.__json, indent=2))

        def json(self):
                return self.__json

        def serialize(self, filePath):
                f = open(filePath, "w")
                f.write(json.dumps(self.__json, indent=2))
                f.close

class JSONModelRelation(metaclass=JSONModel):
        def __init__(self, uri, params = {}, client = None):
                self.uri = uri
                self.client = client or type(self).default_client()
                self.params = params

        def __iter__(self):
                for jm in self.client.get_paged(self.uri, params=self.params):
                        yield JSONModelObject(jm, self.client)

        def __call__(self, myid):
                return JSONModelObject(self.client.get("/".join((self.uri.rstrip("/"), str(myid),))).json(), self.client)

        def __getattr__(self, key):
                return type(self)("/".join((self.uri, key,)), params=self.params, client=self.client)
