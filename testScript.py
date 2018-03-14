from asnake.aspace import ASpace

AS = ASpace()

print (AS.resource(150).title)

for note in AS.resource("150").notes:
	if note.type == "abstract":
		for text in note.content:
			print (text)
			
for ao in AS.resource(151).archival_objects:
	print (ao.title)
	for note in ao.notes:
		note.pp()