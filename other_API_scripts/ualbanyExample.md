# Details about UAlbany draft library

Summary of what I ended up doing. Repo for the actual library is: [https://github.com/UAlbanyArchives/archives_tools](https://github.com/UAlbanyArchives/archives_tools). Everything is fairly well-tested, except exporting EAD is Python3-only for now.

### Principles/Goals

1. Lower the complexity of working with the ArchivesSpace API
2. Write commonly used code once, making it faster and easier to write scripts in the future
3. Be consistent and transparent about what the library is doing
4. Maintain the full functionality of the API in as much as possible

### Decisions

* Used [easydict](https://pypi.python.org/pypi/easydict/) library
	* Can edit JSON with dot syntax
	* Can use BOTH of these
		* resource["extents"][0]["number"]
		* resource.extents[0].number
	* I think this simplifies it a lot, but conflicts with how Python uses objects ¯\\_(ツ)_/¯ 
* Where to put local_settings.cfg?
	* originally put it in the library folder itself
	* moved to `os.path.join(os.getenv("APPDATA"), ".aspaceLibrary")`
		* Seems to work well on Windows and Ubuntu
		* Ubuntu: `~/.aspaceLibrary/local_settings.cfg`
		* Windows: `C:\Users\[user]\AppData\Roaming\.aspaceLibrary\local_settings.cfg`
* What to build-in and whats out of scope
	* e.g. I put in [functions](https://github.com/UAlbanyArchives/archives_tools/blob/master/archives_tools/dacs.py) to convert DACS-style dates with ISO and posix

### Things I think are helpful

* built-in functions to set creds from within library for on-ramping
* Option to use local_settings.cfg or to override it with a tuple
	* e.g. ("http://localhost:8089", "admin", "admin")
	* I did this with an optional param in EVERY function
	* This is useful for development
	* Say I make a script for another archivist with a set robot user, but I don't want to deal with setting up local_settings on their machine
* Both Python 2 and 3 support
	* only barrier I found was in handling Unicode in EAD exporting, and using print()
* Reusable request functions keeps it DRY
	* "single" requests
		*  /repositories/:repo_id/resources/:id
	* "multiple" requests that return list of things with a type and a param
		* /repositories/:repo_id/resources
			* here the "type" would be "resource" and params "all", a range or a set
	* this way you only have to actually use `requests.get()` twice!
* Navigating or exploring functions
	* pretty print to console
	* pretty print to file
	* list all keys in console (for when you can't remember how extents work)
* Functions to make boilerplate objects
	* resources
	* archival_objects

### Things I would do differently

* Rely on local settings for repository number
	* Now it requires, say, "2" in most functions
* Standard machine-actionable response object!
	* I started returning HTTP response as string, e.g. "200"
	* changed inconsistently
	* like for exporting EAD you need it to return the path of the file
	* or when you make a new object it should return its URI

## Functions by type

functions users never see in *italics*

### Navigational functions
* AS.pp()
	* pretty print to console
* AS.serializeOutput()
	* exports to .json
* AS.fields
	* list fields

### Managing Credentials

* *AS.readConfig()*
* *AS.writeConfig()*
* *AS.getLogin()*
* AS.setURL()
* AS.setUser()
* AS.setPassword()
* AS.getSession()


### Utility functions to keep it DRY

* *AS.makeObject()*
	* turns JSON to easydict object
* *AS.checkError()*
	* This need to be changed
	* now just checks if HTTP is 200, if not writes to aspace.log file
* *AS.singleRequest()*
	* Used by many basic functions
* *AS.multipleRequest()*
	* Used by many basic functions
* functions called by *AS.multipleRequest()* (really arn't neccessary)
	* *AS.getResourceList()*
	* *AS.getAccessionList()*
	* *AS.getSubjectList()*
	* *AS.getContainerList()*
	* *AS.getLocationList()*
	* *AS.getDAOList()*


### Resources
* AS.getResources()
	* returns list
* AS.getResource()
* AS.getResourceID()
* AS.getResourcesSince()
	* returns a list of resources updated since ISO param
* AS.makeResource()
	* Makes boilerplate resource object
* AS.postResource()
	* not sure if this is nesseddary or a general postObject() would work by parsing `jsonmodel_type`

### Navigating trees
* *AS.getTree()*
	* just used by getChildren() for resources
* AS.getChildren()
	* list of all children of either resource or archival_objects
	* uses recursive findChild()

### Archival Objects
* AS.getArchObj()
* AS.getArchObjID()
* AS.makeArchObj()
* AS.postArchObj()
	* may not be necessary

### Accessions
* AS.getAccessions()
	* * returns list
* AS.getAccession()
* AS.makeAccession()
* AS.findAccessions()
	* find accessions by title, returns list of uris
* AS.postAccession()

### Extents and Dates
* AS.makeExtent()
* AS.makeDate()

### Notes
* AS.makeSingleNote()
* AS.makeMultiNote()
	* These take a type param, like `scopecontent`, same as the raw JSON
	* Downside is you have to know which not is which

### Subjects
* AS.getSubjects()
	* returns list
* AS.getSubject()
* AS.addSubject()
	* takes a URI
* AS.withSubject()
	* returns list of items with a subject
* probably could use a makeSubject() but I've never needed one


### Containers
* AS.getContainer()
* AS.getContainers()
	* returns a list
* AS.addToContainer()
	* takes a archival object and adds reference to an existing top container via a uri string	
* *AS.makeEmptyContainer()*
	* just used by makeContainer()
* AS.postContainer()
	* post a container object back to Aspace
* AS.makeContainer()

### Locations 
* AS.getLocations()
* AS.getLocation()
* AS.addToLocation()
	* add a location to a container object
* AS.findLocation()
	* Search by title for location and return location URI
* AS.postLocation()

###  Digital Objects
* AS.getDAO()
* AS.getDAOs()
	* returns list
* AS.makeDAO()
	* makes boilerplate DAO
* AS.addDAO()
	* adds a digital object instance to an archival object
* AS.postDAO()

### Exporting
* AS.exportResource()
	* takes resource JSON object and a path and exports EAD-XML
	* Python3 only right now
* AS.exportPDF()
	* takes resource JSON object and a path and exports PDF file
