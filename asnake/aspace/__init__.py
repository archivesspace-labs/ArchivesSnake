from asnake.client import ASnakeClient

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
		
		self.repositories = self.client.get("/repositories").json()
		
		# don't want to do this unless its called
		self.resources = self.getResources()
		
	def getResources(self):
	
		resourceList = self.client.get("/repositories/" + str(self.repository) + "/resources?all_ids=true").json()
		resources = []
		for number in resourceList:
			resource = self.client.get("repositories/" + self.repository + "/resources/" + str(number)).json()
			resources.append(resource)
		return resources

	# sort of just in here for now to help during development
	# I like the idea of including helper functions, but they  probably belong someplace else
	def pp(self, output):
		try:
			print (json.dumps(output, indent=2))
		except:
			import ast
			print (json.dumps(ast.literal_eval(str(output)), indent=2))