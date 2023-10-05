from kafka import KafkaClient
import json
import time
consumer=KafkaClient( bootstrap_servers=["172.16.0.175:9092"], auto_offset_reset="latest",
                                 value_deserializer=lambda m: json.loads(m.decode('utf-8')))

consumer.add_topic("1_104")                  
while True:
    print(consumer.poll())
    time.sleep(1)