"""
Connect with the kafka consumers
"""

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta
from io import BytesIO
from queue import Queue

import cv2
import numpy as np
import requests
from kafka import KafkaConsumer
from PIL import Image
from preprocess.preprocessing import PreProcess
from shared_memory_dict import SharedMemoryDict

# os.environ["SHARED_MEMORY_USE_LOCK"]="1"
postprocess_smd = SharedMemoryDict(name="postprocess", size=10000000)
preprocess_smd = SharedMemoryDict(name="preprocess", size=10000000)
boundary_smd = SharedMemoryDict(name="boundary", size=10000000)



class RawImageConsumer:
    """
    This module fetch data from the topic assigned to the camera
    """

    def __init__(self, kafkashost, cameraid, logger):
        """
        Create instance of Consumer
        Args:
            kafkahost (list): list of url of kafka broker
            cameraid (int):cameraid
            logger (object): logging object
        """
        self.kill = False
        self.camera_id = str(cameraid)
        self.kafkahost = kafkashost
        self.consumer = None
        self.log = logger
        self.postprocess_api=None
        self.check = False
        self.queue_config = None
        # self.preprocess_smd=preprocess_smd
        self.text = None
        self.previous_time = datetime.now()
        data = preprocess_smd[str(cameraid)]
        self.usecaseids = list(data.keys())
        self.topic = data[self.usecaseids[0]]["topic_name"]
        self.log.info(f"Starting for {self.camera_id} and topic {self.topic}")

    def closeConsumer(self):
        """
        Close connection with consumer
        """
        if self.consumer:
            self.consumer.close()
            return True
        else:
            return False

    def connectConsumer(self,postprocss_api):
        """
        Connect with consumer on the assigned topic
        """
        # session_timeout_ms=10000,heartbeat_interval_ms=7000,
        self.queue = Queue(10)
        self.postprocess_api=postprocss_api
        self.consumer = KafkaConsumer(
            "in_" + self.topic,
            bootstrap_servers=self.kafkahost,
            auto_offset_reset="latest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="in_" + self.topic,
        )
        # self.consumer.assign([TopicPartition(self.topic, 1)])
        self.log.info(f"Connected Consumer {self.camera_id} for {self.topic}")

    def isConnected(self):
        """
        Check if consumer is connected
        """
        # print("====Check Self COnsumer====",self.consumer)
        return self.consumer.bootstrap_connected()

    def messageParser(self, msg):
        """
        Parse the message coming from consumer
        returns:
            raw_data (list): list of raw data coming from producer
            imgtime (str): time at which frame is captured
            imagearr (np.array): image as numpy array
        """
        # msg=ast.literal_eval(msg)
        msg = json.loads(msg.value)

        imgtime = datetime.strptime((msg["time"]), "%Y-%m-%d %H:%M:%S.%f")
        raw_data = msg["data"]
        imagestr = msg["image"]
        try:
            stream = BytesIO(imagestr.encode("ISO-8859-1"))
        except Exception as ex:
            stream = BytesIO(imagestr.encode())
        image = Image.open(stream).convert("RGB")
        # print("====imgae===",image)
        imagearr = np.array(image)

        return raw_data, imgtime, imagearr

    def create_packet(
        self,
        timezone,
        preprocess_id,
        schedule_id,
        camera_group_id,
        usecase_id,
        usecase_name,
        image,
        metadata,
        topic_name,
        postprocess,
        split_row,
        split_col,
        boundary=None,
    ):
        """
        create msg packet
        Args:
            timezone (float): timezone offset
            preprocess_id (int): preprocess id
            scehdule_id (int): scheduling id
            camera_group_id (int): camera group id
            usecase_id (int): usecase id
            usecase_name (str):usecase name
            image (np.array): image as numpy array
            meatdata (dict): metadata coming from kafka topic
            topic_name (str): topic name
            postprocess (dict): configuration of postprocess
            boundary (int): boundary data default is None
        returns:
            dict: it contains topic, image, boundary, postprocess configand metadata of camera

        """
        print("===create packet called====")
        image_string = cv2.imencode(".jpg", image)[1].tobytes().decode("ISO-8859-1")
        metadata["usecase"] = {}
        metadata["usecase"]["usecase_id"] = int(usecase_id)
        metadata["usecase"]["name"] = usecase_name
        metadata["time"]["incident_time"]=str(datetime.strptime(metadata["time"]["UTC_time"],"%Y-%m-%d %H:%M:%S.%f")+timedelta(seconds=timezone*60*60))
        metadata["pipeline_inform"] = {}
        metadata["pipeline_inform"]["preprocess_id"] = preprocess_id
        metadata["pipeline_inform"]["schedule_id"] = schedule_id
        metadata["pipeline_inform"]["camera_group_id"] = camera_group_id
        print("======packet done")
        postprocess["split_image"]={"split_row":split_row,"split_col":split_col}

        return {
            "image": image_string,
            "topic_name": topic_name,
            "metadata": metadata,
            "postprocess_config": postprocess,
            "boundary_config": boundary,
        }
    def multiple_consumer(self):
        thread_executor=ThreadPoolExecutor(max_workers=4)
        thread_executor_list=[]
        for i in range(0,4):
            f1=thread_executor.submit(self.runConsumer)
            thread_executor_list.append(f1)
        return thread_executor_list

    def runConsumer(self):
        """
        Run consumer and fetch data from kafka topics
        """
        print(f"=={self.camera_id} Message Parse Connected for Topic {self.topic}====")
        self.check = True

        self.log.info(f"Starting Message Parsing {self.camera_id} for {self.topic}")
        
        for message in self.consumer:
            # print("====Frame received===")
            if self.camera_id in list(preprocess_smd.keys()):
                data = preprocess_smd[str(self.camera_id)]
                # print("====data===",data)
                usecase = []
                usecase = list(data.keys())
                print("********usecase for camera*******", self.camera_id,usecase)
                
                
                self.previous_time = datetime.now()
                raw_data, imgtime, image = self.messageParser(message)
                fetchtime = (datetime.now() - imgtime).total_seconds()
                print(f"Fetch time {self.camera_id} is", fetchtime)
                self.log.info(f"Fetch Time for {self.camera_id} is {fetchtime}")
                
                for i in usecase:
                    if preprocess_smd[self.camera_id][str(i)]["current_state"]:
                        timezone=float(preprocess_smd[self.camera_id][str(i)]["timezone_offset"])
                        
                        split_row=1
                        split_col=1

                        if str(i) in list(data.keys()):
                            if data[str(i)]["preprocess_id"] is not None:
                                pp = PreProcess()

                                preprocess_config_data = preprocess_smd[str(self.camera_id)][str(i)]
                                if preprocess_config_data["split_process_row"] is not None and preprocess_config_data["split_process_row"]>0:
                                    split_row=preprocess_config_data["split_process_row"]
                                if preprocess_config_data["split_process_column"] is not None and preprocess_config_data["split_process_column"]>0:
                                    split_col=preprocess_config_data["split_process_column"]

                                image = np.array(pp.process(image, preprocess_config_data))
                            if str(i) in list(postprocess_smd.keys()):
                                postprocess_config = postprocess_smd[str(i)]
                                try:
                                    boundary_config = boundary_smd[str(self.camera_id)][str(i)]
                                except KeyError as ex:
                                    boundary_config = None

                                #print("===postprocess for vamera id===", self.camera_id, i)

                                data_packet = self.create_packet(
                                    timezone,
                                    data[str(i)]["preprocess_id"],
                                    "",
                                    data[str(i)]["camera_group_id"],
                                    i,
                                    data[str(i)]["usecase_name"],
                                    image,
                                    raw_data,
                                    self.topic,
                                    postprocess_config,
                                    split_row,
                                    split_col,
                                    boundary_config,
                                )

                                try:
                                    print("=====calling api===")
                                    response = requests.post(
                                        self.postprocess_api, json=data_packet, timeout=5
                                    )
                                    self.log.info(f"Postprocessing called for cameraid {self.camera_id} and usecase_id {i}")
                                    print(f"Postprocessing called for cameraid {self.camera_id} and usecase_id {i}")
                                except Exception as ex:
                                    self.log.info(f"Exception called for cameraid {self.camera_id} and usecase_id {i} exception {ex}")
                                    print(f"Exception called for cameraid {self.camera_id} and usecase_id {i} exception {ex}")
                            

                        

    def callConsumer(self):
        print(self.runConsumer())

    def killTopic(self):
        self.kill = True

   
