import redis
import json
pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
r = redis.Redis(connection_pool=pool)
data=r.get("preprocess")
print("===============PreProcess Cache Data========")

jsondata=json.loads(data)

print(jsondata['6'])

