from asnake.aspace import ASpace

AS = ASpace()
repo = AS.repositories(2)

print (repo.resources(150).title)
"""
for collection in repo.resources:
	print (collection.title)


# I think we should add these in somehow, maybe namespaced
print (repo.resourceID("apap101").title)
record = AS.archival_object("610555991d1ab7559c835ab7cac38bcf")


#seems a hair slower than I'd expect, but I think it might just be me/my setup
print (repo.archival_objects(210664).title)

#for obj in repo.archival_objects:
	#print (obj.title)



record = repo.archival_objects(25720)

for note in record.notes:
	if note.type == "scopecontent":
		print (note.json())

for accession in repo.accessions:
	print (accession.title)
	if "2007" in accession.accession_date:
		print (accession.json())


for person in AS.agents.people:
	print (person.title)
	

AS.agents.people(115).pp()


for note in repo.resources("150").notes:
	if note.type == "abstract":
		note.pp()
		#print (note) #AWESOME that this returns the actual ASpace model name
		#object might not be recursive
		#for text in note.content:
			#print (text)
			
#doesn't work, I think we can do it better than I had it anyway
for ao in repo.resources(151).archival_objects:
	print (ao.title)
	for note in ao.notes:
		note.pp()
		

for spot in AS.locations:
	print (spot.building + " " + spot.floor + " " + spot.area)
"""