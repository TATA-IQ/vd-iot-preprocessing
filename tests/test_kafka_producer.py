from kafka import KafkaProducer
import json
import time
#"172.16.0.171:9092","172.16.0.175:9092"
producer = KafkaProducer(bootstrap_servers="172.16.0.175:9092", value_serializer=lambda x: json.dumps(x).encode('utf-8'))
dictdata={}
for i in range(0,100):
    dictdata["a"]="b"
    json_object = json.dumps(dictdata, indent=4)
    print(json_object)

    producer.send("1_1", value=dictdata)
    producer.send("1_1", value=dictdata)
    producer.send("1_1", value=dictdata)
    producer.send("1_1", value=dictdata)
    time.sleep(1)