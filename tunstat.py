import pymongo
import os

db = pymongo.MongoClient().coyote

while True:
	blx = list(db.blocks.find())
	print "There are %d tunnels", len(blx)
	for b in blx:
		print "pinging %s for block %s" % (b["client_router6"],b["ip6"])
		res = os.system("ping6 -c 4 "+b["client_router6"])
		print "res was: ",res
