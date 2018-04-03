from asnake.client import ASnakeClient
from asnake.jsonmodel import JSONModelObject, JSONModelRelation
from itertools import chain
import json
import re

class ASpace():

        # this happens when you call ASpace()
        def __init__(self, **config):
                # Repository will default to 2 if not provided
                self.repository = config.pop('repository', '2')

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
                        # This sets plural attributes, like resources and archival_objects
                        # Not sure if this is safe
                        if attr.lower().endswith("s"):
                                shortCalls = ["repositories", "locations", "subjects", "users", "vocabularies", "location_profiles", "container_profiles"]
                                #for calls without repositories in them
                                if attr in shortCalls:
                                        return JSONModelRelation(self.__client.get("/" + str(attr), params= {"all_ids": True}).json(), self.__client, self.repository, attr)
                                else:
                                        return JSONModelRelation(self.__client.get("/repositories/" + str(self.repository) + "/" + str(attr), params={"all_ids": True}).json(), self.__client, self.repository, attr)

        @property
        def resources(self):
                '''return all resources from every repo'''
                repo_uris = [r['uri'] for r in self.__client.get('repositories').json()]
                for resource in chain(*[self.__client.get_paged('{}/resources'.format(uri)) for uri in repo_uris]):
                        yield JSONModelObject(resource, self.__client)


        # not sure if theres a way to pass a variable to implement this with __getattr__
        def resource(self, id):
                return JSONModelObject(self.__client.get("repositories/" + self.repository + "/resources/" + str(id)).json(), self.__client)

        #this doesn't work yet
        def resourceID(self, id):
                result = self.__client.get("/repositories/" + self.repository + "/search?page=1&aq={\"query\":{\"field\":\"identifier\", \"value\":\"" + str(id) + "\", \"jsonmodel_type\":\"field_query\"}}").json()
                resourceURI = result["results"][0]["uri"]
                return JSONModelObject(self.__client.get(resourceURI).json(), self.__client)

        def archival_object(self, id):
                if isinstance(id, str):
                        if len(id) == 32:
                                # its a ref_id
                                params = {"ref_id[]": str(id)}
                                refList = self.__client.get("repositories/" + self.repository + "/find_by_id/archival_objects?page=1&ref_id[]=" + str(id)).json()
                                return JSONModelObject(self.__client.get(refList["archival_objects"][0]["ref"]).json(), self.__client)
                #its a uri number
                return JSONModelObject(self.__client.get("repositories/" + self.repository + "/archival_objects/" + str(id)).json(), self.__client)

        def agents(self, type, id = None):
                if id == None:
                        return JSONModelRelation(self.__client.get("/agents/" + str(type) + "?all_ids=true").json(), self.__client, self.repository, type)
                else:
                        return JSONModelObject(self.__client.get("/agents/" + str(type) + "/" + str(id)).json(), self.__client)
