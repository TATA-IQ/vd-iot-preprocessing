from kafka import KafkaConsumer
from concurrent.futures import ThreadPoolExecutor
import cv2
import numpy as np
import json
import base64
import threading
import redis
import time
from datetime import datetime
import os
import requests
import ast
import gc
from preprocess.preprocessing import PreProcess
from queue import Queue
from kafka import TopicPartition
from shared_memory_dict import SharedMemoryDict
from PIL import Image
from io import BytesIO
# os.environ["SHARED_MEMORY_USE_LOCK"]="1"
postprocess_smd = SharedMemoryDict(name='postprocess', size=10000000)
preprocess_smd = SharedMemoryDict(name='preprocess', size=10000000)
boundary_smd = SharedMemoryDict(name='boundary', size=10000000)
class RawImageConsumer():
    def __init__(self,kafkashost,cameraid,logger):
        self.kill=False
        self.camera_id=str(cameraid)
        self.kafkahost=kafkashost
        self.consumer=None
        self.log=logger
        self.check=False
        self.queue_config=None
        #self.preprocess_smd=preprocess_smd
        self.text=None
        self.previous_time=datetime.now()
        data=preprocess_smd[str(cameraid)]
        self.usecaseids= list(data.keys())
        self.topic=data[self.usecaseids[0]]["topic_name"]
        self.log.info(f"Starting for {self.camera_id} and topic {self.topic}")
        
    def closeConsumer(self):
        if self.consumer:
            self.consumer.close()
            return True
        else:
            return False
    
    def connectConsumer(self):
        
        #session_timeout_ms=10000,heartbeat_interval_ms=7000,
        self.queue=Queue(100)
        self.consumer=KafkaConsumer("in_"+self.topic, bootstrap_servers=self.kafkahost, auto_offset_reset="latest",
                                 value_deserializer=lambda m: json.loads(m.decode('utf-8')),group_id=self.topic)
        #self.consumer.assign([TopicPartition(self.topic, 1)])
        self.log.info(f"Connected Consumer {self.camera_id} for {self.topic}")

    
        
    def isConnected(self):
        #print("====Check Self COnsumer====",self.consumer)
        return self.consumer.bootstrap_connected()
    def messageParser(self,msg):
        #msg=ast.literal_eval(msg)
        msg=json.loads(msg.value)
        
        imgtime=datetime.strptime((msg["time"]),"%Y-%m-%d %H:%M:%S.%f")
        raw_data=msg["data"]
        imagestr=msg["image"]
        try:
            stream = BytesIO(imagestr.encode("ISO-8859-1"))
        except Exception as ex:
            
            stream = BytesIO(imagestr.encode())
        image = Image.open(stream).convert("RGB")
        # print("====imgae===",image)
        imagearr=np.array(image)

 


        return raw_data,imgtime,imagearr

    def create_packet(self,preprocess_id,schedule_id,camera_group_id,usecase_id,usecase_name,image,metadata,topic_name,postprocess,boundary=None):
        print("===create packet called====")
        image_string = cv2.imencode(".jpg", image)[1].tobytes().decode("ISO-8859-1")
        metadata["usecase"]={}
        metadata["usecase"]["id"]=usecase_id
        metadata["usecase"]["name"]= usecase_name
        metadata["pipeline_inform"]={}
        metadata["pipeline_inform"]["preprocess_id"]=preprocess_id
        metadata["pipeline_inform"]["schedule_id"]=schedule_id
        metadata["pipeline_inform"]["camera_group_id"]=camera_group_id
        print("======packet done")
        
        return {"image":image_string, "topic_name":topic_name,"metadata":metadata,"postprocess_config":postprocess,"boundary_config":boundary}



    
    def runConsumer(self):
        
        

        print(f"=={self.camera_id} Message Parse Connected for Topic {self.topic}====")
        self.check=True 
        
        self.log.info(f"Starting Message Parsing {self.camera_id} for {self.topic}")
        # while True:
        #     print(self.consumer)
        for message in self.consumer:
            print("====Frame received===")
            if self.camera_id in list(preprocess_smd.keys()):
                data=preprocess_smd[str(self.camera_id)]
                # print("====data===",data)
                usecase=list(data.keys())
                fetchtime=(datetime.now()-self.previous_time).total_seconds()
                self.previous_time=datetime.now()
                raw_data,imgtime,image=self.messageParser(message)
                fetchtime=(datetime.now()-imgtime).total_seconds()
                print(f"Fetch time {self.camera_id} ",fetchtime)
                self.log.info(f"Fetch Time for {self.camera_id} {fetchtime}")
                #time.sleep(0.0001)
                #yield "abc"
                for i in usecase:
                    
                    if str(i) in list(data.keys()):
                        if data[str(i)]["preprocess_id"] is not None:
                            pp=PreProcess()
                            
                            #print(self.preprocess_smd)
                            preprocess_config_data=preprocess_smd[str(self.camera_id)][str(i)]
                            image=np.array(pp.process(image,preprocess_config_data))
                            
                        
                        if str(i) in list(postprocess_smd.keys()):
                            postprocess_config=postprocess_smd[str(i)]
                            try:
                                boundary_config=boundary_smd[str(self.camera_id)][str(i)]
                            except Exception as ex:
                                boundary_config=None
                            
                            print("===postprocess for vamera id===",self.camera_id)
                            # print(preprocess_smd[str(self.camera_id)][str(i)])
                            data_packet=self.create_packet(data[str(i)]["preprocess_id"],"",data[str(i)]["camera_group_id"],i,data[str(i)]["usecase_name"],image,raw_data,self.topic,postprocess_config,boundary_config)
                            #json_data=json.loads(data_packet)
                            # print(data_packet)
                            try:
                                response=requests.post("http://172.16.0.204:8005/postprocess",json=data_packet, timeout=5)
                                print(f"camera id {self.camera_id} usecase_id {i}")
                                print(response.text,"8005")
                            except Exception as ex:
                                print("****",ex)
                                print("Timout 8005")
                            try:
                                response=requests.post("http://localhost:8006/postprocess",json=data_packet, timeout=5)
                                
                                print(f"camera id {self.camera_id} usecase_id {i}")
                                print(response.text,"8006")
                            except:
                                print("Timeout on 8006")
                            try:
                                response=requests.post("http://localhost:8007/postprocess",json=data_packet, timeout=5)
                                
                                print(f"camera id {self.camera_id} usecase_id {i}")
                                print(response.text,"8007")
                            except:
                                print("Timeout on 8007")
                            del data_packet
            gc.collect()

                        # except Exception as ex:
                        #     print("===exception===",ex)
                        #     print(data[str(i)])
            # time.sleep(5)
                    
                    



                    
    
            
    def callConsumer(self):
        print(self.runConsumer())



    def killTopic(self):
        self.kill=True
    
    # def preProcessData(self):
    #     pass