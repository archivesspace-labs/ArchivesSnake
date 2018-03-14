from asnake.client import ASnakeClient
import json

class ASpace():

	#pass repository when instantiated?
	def __init__(self, repository=None):
	
		#repository default to 2 if not provided?
		if repository == None:
			self.repository = "2"
		else:
			self.repository = repository
			
		self.__client = ASnakeClient()
		self.__client.authorize()
		
		
	def __getattr__(self, attr):
		if attr == "repositories":
			return jsonmodel_muliple_object(self.__client.get("/repositories").json(), self.__client)
		else:
			return jsonmodel_muliple_object(self.__client.get("/repositories/" + str(self.repository) + "/" + str(attr) + "?all_ids=true").json(), self.__client)

	# not sure how to pass a variable to implement this with __getattr__
	def resource(self, id):
		resource = self.__client.get("repositories/" + self.repository + "/resources/" + str(id)).json()	
		return jsonmodel_single_object(resource, self.__client)
	
		
class jsonmodel_single_object:
	def __init__(self, json_rep, client = None):
		self.__json = json_rep
		self.__client = client
	
	def __getattr__(self, key):
	
		#for testing
		#print (key)
		if isinstance(key, str):
			if not key.startswith('_'):
				if not key in self.__json.keys():
					repository = self.__json["repository"]["ref"].split("/repositories/")[1]
					return jsonmodel_muliple_object(self.__json, self.__client)
		
		if isinstance(self.__json[key], list):
			return jsonmodel_muliple_object(self.__json[key], self.__client)
		elif isinstance(self.__json[key], str):
			return self.__json[key]
		elif isinstance(self.__json[key], dict):
			return jsonmodel_single_object(self.__json[key], self.__client)


	# utility methods
	def pp(self):
		print (json.dumps(self.__json, indent=2))

	def json(self):
		return self.__json

	def serialize(self, filePath):
		f = open(filePath, "w")
		f.write(json.dumps(self.__json, indent=2))
		f.close

class jsonmodel_muliple_object:

	def __init__(self, json_list, client, repository=None, call=None):
		self.__client = client
	
		self.list = []
		if isinstance(json_list, list):
			for item in json_list:
				if isinstance(item, str):
					self.list.append(item)
				if isinstance(item, int):
					object = self.__client.get("repositories/" + repository + "/" + call + "/" + str(item)).json()	
					self.list.append(jsonmodel_single_object(object))
				else:
					self.list.append(jsonmodel_single_object(item))
		else:
			# for trees
			# check if resource or archival_object
			if json_list["jsonmodel_type"] == "resource":
				tree = self.__client.get(json_list["uri"] + "/tree").json()["children"]
				childList = []
				for child in tree:
					childObject = self.__client.get(child["record_uri"]).json()
					self.list.append(jsonmodel_single_object(childObject, self.__client))
			else:
				tree = self.__client.get(json_list["resource"]["ref"] + "/tree").json()["children"]
				childList = []
				for child in findChild(tree, json_list["uri"], None):
					self.list.append(jsonmodel_single_object(self.__client.get(child["record_uri"]).json(), self.__client))	

	# this finds children within trees
	def findChild(tree, uri, childrenObject):
		for child in tree["children"]:
			if child["record_uri"] == uri:
				childrenObject = makeObject(child)
			elif len(child["children"]) < 1:
				pass
			else:
				childrenObject = findChild(child, uri, childrenObject)
		return childrenObject
			
	def __iter__(self):
		return iter(self.list)