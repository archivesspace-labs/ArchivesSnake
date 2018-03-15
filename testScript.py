from asnake.aspace import ASpace

AS = ASpace()

for repo in AS.repositories:
    print (repo.name)

print (AS.resource(150).title)

print (AS.archival_object(219664).title)

record = AS.archival_object("f53f04ab07334848b101318eebb7c300")

for extent in record.extents:
	print (extent.number + " " + extent.extent_type)



"""
for note in AS.resource("150").notes:
	if note.type == "abstract":
		for text in note.content:
			print (text)
			
for ao in AS.resource(151).archival_objects:
	print (ao.title)
	for note in ao.notes:
		note.pp()
		
for collection in AS.resources:
	print (collection.title)
"""