# Classes dealing with JSONModel imports
class JSONModelObject:
        '''A wrapper over the JSONModel representation of a single object in ArchivesSpace.'''
        __default_client = None

        @classmethod
        def default_client(cls):
            if not cls.__default_client:
                    from asnake.client import ASnakeClient
                    cls.__default_client = ASnakeClient()
            return __default_client

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
                self.reify()
                result = "#<JSONModel:{}".format(self.__json['jsonmodel_type'])

                if 'uri' in self.__json:
                        result += ':' + self.uri
                return result + '>'

        def __getattr__(self, key):
                '''Access to properties on the JSONModel object. '''
                self.reify()
                if not key.startswith('_'):
                        if not key in self.__json.keys():
                                repository = self.__json["repository"]["ref"].split("/repositories/")[1]
                                return JSONModelRelation(self.__json, self.__client)

                if isinstance(self.__json[key], list):
                        return JSONModelRelation(self.__json[key], self.__client)
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


#Returns a generator object to stream lists of objects
def JSONModelRelation(json_list, client, repository=None, call=None):

        if isinstance(json_list, list):
                #this is for a list of ids to call
                for item in json_list:
                        if isinstance(item, str):
                                yield item
                        if isinstance(item, int):
                                #check for agents, because its a different call
                                shortCalls = ["locations", "subjects", "users", "vocabularies", "location_profiles", "container_profiles"]
                                agentTypes = ["corporate_entities", "families", "people", "software"]
                                if call in shortCalls:
                                        object = client.get(call + "/" + str(item)).json()
                                elif call in agentTypes:
                                        object = client.get("agents/" + call + "/" + str(item)).json()
                                else:
                                        object = client.get("repositories/" + repository + "/" + call + "/" + str(item)).json()
                                yield JSONModelObject(object, client)
                        else:
                                yield JSONModelObject(item, client)

        else:
                        # for trees, like a list of children
                        # check if resource or archival_object
                        if json_list["jsonmodel_type"] == "resource":
                                tree = client.get(json_list["uri"] + "/tree").json()["children"]
                                for child in tree:
                                        childObject = client.get(child["record_uri"]).json()
                                        yield JSONModelObject(childObject, client)
                        else:
                                tree = client.get(json_list["resource"]["ref"] + "/tree").json()["children"]
                                for child in findChild(tree, json_list["uri"], None):
                                        yield JSONModelObject(lient.get(child["record_uri"]).json(), client)

# this finds children within trees
# I think there's better ways of doing this in 2.0+
def findChild(tree, uri, childrenObject):
        for child in tree["children"]:
                if child["record_uri"] == uri:
                        childrenObject = makeObject(child)
                elif len(child["children"]) < 1:
                        pass
                else:
                        childrenObject = findChild(child, uri, childrenObject)
        return childrenObject
