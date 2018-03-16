from asnake.client import ASnakeClient
import json

class ASpace():

	# this happens when you call ASpace()
	def __init__(self, repository=None):
		
		# Repository will default to 2 if not provided
		if repository == None:
			self.repository = "2"
		else:
			self.repository = repository
		
		# Connect to ASpace using .archivessnake.yml
		self.__client = ASnakeClient()
		self.__client.authorize()
		
		self.version = self.__client.get("/version").text.split("(v")[1].split(")")[0]
	
	# this automatically sets attributes to ASpace(), so you can ASpace().resources, etc.	
	def __getattr__(self, attr):
		if not attr.startswith('_'):
			# This sets plural attributes, like resources and archival_objects
			# Not sure if this is safe
			if attr.lower().endswith("s"):
				shortCalls = ["repositories", "locations", "subjects", "users", "vocabularies", "location_profiles", "container_profiles"]
				#for calls without repositories in them
				if attr in shortCalls:
					return jsonmodel_muliple_object(self.__client.get("/" + str(attr) + "?all_ids=true").json(), self.__client, self.repository, attr)
				else:
					return jsonmodel_muliple_object(self.__client.get("/repositories/" + str(self.repository) + "/" + str(attr) + "?all_ids=true").json(), self.__client, self.repository, attr)

	# not sure if theres a way to pass a variable to implement this with __getattr__
	def resource(self, id):
		return jsonmodel_single_object(self.__client.get("repositories/" + self.repository + "/resources/" + str(id)).json(), self.__client)
	
	#this doesn't work yet
	def resourceID(self, id):
		result = self.__client.get("/repositories/" + self.repository + "/search?page=1&aq={\"query\":{\"field\":\"identifier\", \"value\":\"" + str(id) + "\", \"jsonmodel_type\":\"field_query\"}}").json()
		resourceURI = result["results"][0]["uri"]
		return jsonmodel_single_object(self.__client.get(resourceURI).json(), self.__client)		
		
	def archival_object(self, id):
		if isinstance(id, str):
			if len(id) == 32:
				# its a ref_id
				params = {"ref_id[]": str(id)}
				refList = self.__client.get("repositories/" + self.repository + "/find_by_id/archival_objects?page=1&ref_id[]=" + str(id)).json()
				return jsonmodel_single_object(self.__client.get(refList["archival_objects"][0]["ref"]).json(), self.__client)
		#its a uri number
		return jsonmodel_single_object(self.__client.get("repositories/" + self.repository + "/archival_objects/" + str(id)).json(), self.__client)
	
	def agents(self, type, id = None):
		if id == None:
			return jsonmodel_muliple_object(self.__client.get("/agents/" + str(type) + "?all_ids=true").json(), self.__client, self.repository, type)
		else:
			return jsonmodel_single_object(self.__client.get("/agents/" + str(type) + "/" + str(id)).json(), self.__client)

		
class jsonmodel_single_object:
	def __init__(self, json_rep, client = None):
		self.__json = json_rep
		self.__client = client
	
	def __getattr__(self, key):
	
		if isinstance(key, str):
			if not key.startswith('_'):
				if not key in self.__json.keys():
					repository = self.__json["repository"]["ref"].split("/repositories/")[1]
					return jsonmodel_muliple_object(self.__json, self.__client)
		
		if isinstance(self.__json[key], list):
			return jsonmodel_muliple_object(self.__json[key], self.__client)
		elif isinstance(self.__json[key], dict):
			return jsonmodel_single_object(self.__json[key], self.__client)
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
def jsonmodel_muliple_object(json_list, client, repository=None, call=None):

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
				yield jsonmodel_single_object(object)
			else:
				yield jsonmodel_single_object(item)
				
	else:
			# for trees, like a list of children
			# check if resource or archival_object
			if json_list["jsonmodel_type"] == "resource":
				tree = client.get(json_list["uri"] + "/tree").json()["children"]
				for child in tree:
					childObject = client.get(child["record_uri"]).json()
					yield jsonmodel_single_object(childObject, client)
			else:
				tree = client.get(json_list["resource"]["ref"] + "/tree").json()["children"]
				for child in findChild(tree, json_list["uri"], None):
					yield jsonmodel_single_object(lient.get(child["record_uri"]).json(), client)

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