import redis
import json
pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
r = redis.Redis(connection_pool=pool)
data=r.get("boundary")
print("===============PreProcess Cache Data========")
print(data)

jsondata=json.loads(data)
print("===========")
print(jsondata["10"])
