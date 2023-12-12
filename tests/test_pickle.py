import json 
from kafka import KafkaConsumer
import pickle
from shared_memory_dict import SharedMemoryDict
class JSONSerializer:
    def dumps(self, obj) -> bytes:
        try:
            return json.dumps(obj).encode() + NULL_BYTE
        except Exception as ex:
            print(ex)
            #raise SerializationError(obj)

    def loads(self, data: bytes) -> dict:
        data = data.split(NULL_BYTE, 1)[0]
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise DeserializationError(data)
consumer=KafkaConsumer("test", bootstrap_servers=["172.16.0.175:9092"], auto_offset_reset="latest",
                                 value_deserializer=lambda m: json.loads(m.decode('utf-8')))
# pickle.dump(consumer)
with open("test.pickle", "wb") as outfile:
    pickle.dumps(consumer, outfile)
# smd = SharedMemoryDict(name='tokens3', size=1024)
# smd["a"]=consumer
print("===>",smd)
# JSONSerializer().dumps(consumer)