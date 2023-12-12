import redis
import json

pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
r = redis.Redis(connection_pool=pool)
data = r.get("cameraconf")
print("===============PreProcess Cache Data========")
jsondata = json.loads(data)
print(jsondata)

# del jsondata["5"]
# print(jsondata["1"].keys())
# r.set("cameraconf", json.dumps(jsondata))
