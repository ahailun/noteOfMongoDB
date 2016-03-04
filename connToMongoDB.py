from pymongo import MongoClient
import time

db = MongoClient().performance_test
db.drop_collection("updates")
collection = db.updates
collection.insert({"x": 1})

collection.find_one()

start = time.time()
for i in range(10000):
    collection.update({'x': 1}, {"$inc": {"x": 1}})
print "used time:", time.time()-start
