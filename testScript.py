from asnake.aspace import ASpace

AS = ASpace()

for repo in AS.repositories:
    print (repo.name)

print (AS.resource(150).title)

print (AS.resourceID("apap101").title)

print (AS.archival_object(219664).title)
"""
record = AS.archival_object("610555991d1ab7559c835ab7cac38bcf")

record.extents[0].pp()

for note in record.notes:
	print (note.subnotes[0].publish)
"""
for agent in AS.agents("people"):
	print (agent.title)

#AS.agents("people", 115).pp()



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