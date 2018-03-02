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
			
		self.client = ASnakeClient()
		self.client.authorize()
		
		
	def __getattr__(self, attr):
		if attr == "repositories":
			repoList = []
			for repo in self.client.get("/repositories").json():
				repoList.append(Thing(repo))
			return repoList
		
		if attr == "resources":
			resourceList = self.client.get("/repositories/" + str(self.repository) + "/resources?all_ids=true").json()
			resources = []
			for number in resourceList:
				resource = self.client.get("repositories/" + self.repository + "/resources/" + str(number)).json()
				resources.append(Thing(resource))
			return resources
			
	def resource(self, id):
		resource = self.client.get("repositories/" + self.repository + "/resources/" + str(id)).json()
		
		
		return Thing(resource)
	
	
	#just for testing
	def pp(self, output):
		try:
			print (json.dumps(output, indent=2))
		except:
			import ast
			print (json.dumps(ast.literal_eval(str(output)), indent=2))
		
			
class Thing():
	def __init__(self, jsonObject):
		self.__json = jsonObject
	
		return thingify(jsonObject)
	
	def thingify(jsonObject):
		fieldList = []
		for field in jsonObject.keys():
			fieldList.append(field)
			setattr(self, field, jsonObject[field])
		setattr(self, "fields", fieldList)
		
class jsonmodel_single_object:
	def __init__(self, json_rep):
		self.__json = json_rep

	def __getattr__(self, key):
		if is_single_obj(self.__json[key]):
			return jsonmodel_single_object(self.__json[key])
		else if # case for plural
			# return mapping object for collection
			pass
		else if # is a simple value
			return self.__json[key]

	def __setattr__(self, key, value):
		 if not key.startswith('_'):
			  # discern what's getting passed, set things and stuff
		