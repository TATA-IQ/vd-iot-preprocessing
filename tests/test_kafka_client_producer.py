from kafka import KafkaClient
import json
import time
producer=KafkaClient( bootstrap_servers=["172.16.0.175:9092"], auto_offset_reset="latest",
                                 value_deserializer=lambda m: json.loads(m.decode('utf-8')))

producer.add_topic("1_104") 
dictdata={}
for i in range(0,100):
    dictdata["a"]="b"
    json_object = json.dumps(dictdata, indent=4)
    print(json_object)

    producer.send("1_20", dictdata)
    time.sleep(1)