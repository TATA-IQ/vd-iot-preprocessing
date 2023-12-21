from kafka import KafkaConsumer
import json
consumer=KafkaConsumer("in_2_4_6", bootstrap_servers=["172.16.0.175:9092"], auto_offset_reset="latest",
                                 value_deserializer=lambda m: json.loads(m.decode('utf-8')))
                    
for msg in consumer:
    print(msg.value)