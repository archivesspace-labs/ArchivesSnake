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
			return jsonmodel_muliple_object(self.__client.get("/repositories").json())
		else:
			return jsonmodel_muliple_object(self.__client.get("/repositories/" + str(self.repository) + "/" + str(attr) + "?all_ids=true").json())

	def resource(self, id):
		resource = self.__client.get("repositories/" + self.repository + "/resources/" + str(id)).json()
		
		
		return jsonmodel_single_object(resource, self.__client)
	
		
class jsonmodel_single_object:
	def __init__(self, json_rep, client = None):
		self.__json = json_rep
		self.__client = client


	def __getattr__(self, key):

		if isinstance(key, str):
			if not key.startswith('_'):
				if not key in self.__json.keys():
					return jsonmodel_muliple_object(self.__client.get("/repositories/" + str(self.repository) + "/" + str(key) + "?all_ids=true").json())
		
		if isinstance(self.__json[key], list):
			return jsonmodel_muliple_object(self.__json[key])
		elif isinstance(self.__json[key], str):
			return self.__json[key]
		elif isinstance(self.__json[key], dict):
			return jsonmodel_single_object(self.__json[key], self.__client)



	def pp(self):
		return json.dumps(self.__json, indent=2)

	def json(self):
		return self.__json

	def serialize(self, filePath):
		f = open(filePath, "w")
		f.write(json.dumps(self.__json, indent=2))
		f.close

class jsonmodel_muliple_object:

	def __init__(self, json_list):
		self.list = []
		for item in json_list:
			if isinstance(item, str):
				self.list.append(item)
			else:
				self.list.append(jsonmodel_single_object(item))
	def __iter__(self):
		return iter(self.list)