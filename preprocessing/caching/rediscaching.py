"""
Redis Caching
"""
import json
import threading
from datetime import datetime
import time
import redis
import requests
from caching.boundary_caching import PersistBoundaryConfig
from caching.postprocess_caching import PersistPostProcessConfig
from caching.preprocess_caching import PersistPreprocessConfig
from caching.schedule_caching import PersistSchedule
from kafka import KafkaConsumer
from console_logging.console import Console
console=Console()


class Caching:
    """
    This class handles the caching of the respective module
    And always listens for the event changes in kafka.
    If any event is encountered it will update the caching.
    """

    def __init__(
        self,
        api: dict,
        redisconf:dict,
        camera_group: list = None,
        customer: list = None,
        location: list = None,
        subsite: list = None,  # noqa: E501
        zone: list = None,
    ) -> None:  # noqa: E501
        """
        Initialize the caching
        Args:
            api (dict): dict of apis
            customer (list): list of customer id, by default is None
            location (list): list of customer id, by default is None
            subsite (list): list of subsite id, by default is None
            camera_group (list): list of camera group, by default is None
        """
        pool = redis.ConnectionPool(host=redisconf["host"], port=redisconf["port"], db=0)
        self.r = redis.Redis(connection_pool=pool)
        print("customer", customer)
        print("location", location)
        print("subsite", subsite)
        print("zone", subsite)
        print("camera_group", camera_group)
        self.customer = customer
        self.camera_group = camera_group
        self.location = location
        self.subsite = subsite
        self.zone = zone
        self.schedule = PersistSchedule(api["schedule_master"])
        self.preprocs = PersistPreprocessConfig(api["preprocess_config"])

        self.api = api
        self.postprocess = PersistPostProcessConfig(self.api)
        self.boundary = PersistBoundaryConfig(self.api)
        # self.urllist=urllist

    def get_cam_group(
        self,
        customer: list = None,
        location: list = None,
        subsite: list = None,
        zone: list = None,
        camera_group: list = None,  # noqa: E501
    ) -> list:  # noqa: E501
        """
        Get all the camera group based on the params
        Args:
            customer (list): list of customer id, by default is None
            location (list): list of customer id, by default is None
            subsite (list): list of subsite id, by default is None
            zone (list): list of zone id, by default is None
            camera_group (list): list of camera group, by default is None
        returns:
            camgroup (list): All the cameragroup
        """
        camgroup = []
        if (
            customer is None and location is None and subsite is None and camera_group is None and zone is None
        ):  # noqa: E501
            r = requests.get(self.api["camera_group"], timeout=50)
            try:
                camgroup = r.json()["data"]
            except Exception as ex:
                console.error(f"Camgroup exception: {0}".format(ex))
                return []

        if customer is not None:
            r = requests.get(self.api["camera_group"], json={"customer_id": customer}, timeout=50)  # noqa: E501
            try:
                camgroup = r.json()["data"]
                # print("===customer==",camgroup)
            except Exception as ex:
                console.error(f"Exceptin while fetching customer {0}".format(ex))
                pass
        if location is not None:
            r = requests.get(self.api["camera_group"], json={"location_id": location}, timeout=50)  # noqa: E501
            try:
                if len(camgroup) > 0:
                    camgroup = camgroup + r.json()["data"]
                    
            except Exception as ex:
                console.error(f"Exceptin while fetching location {0}".format(ex))
                pass
        if subsite is not None:
            r = requests.get(self.api["camera_group"], json={"subsite_id": subsite}, timeout=50)  # noqa: E501
            try:
                if len(camgroup) > 0:
                    camgroup = camgroup + r.json()["data"]
                   
            except Exception as ex:
                console.error(f"Exceptin while fetching subsite {0}".format(ex))
                pass
        if zone is not None:
            r = requests.get(self.api["camera_group"], json={"zone_id": zone}, timeout=50)  # noqa: E501
            try:
                if len(camgroup) > 0:
                    camgroup = camgroup + r.json()["data"]
                    
            except Exception as ex:
                console.error(f"Exceptin while fetching zone {0}".format(ex))
                pass

        return list(set(camgroup))

    def persist_data(self):
        """
        Save Data To cache
        """
        camgroup_conf=None
        while True:
            try:
                camgroup_conf = self.get_cam_group(self.customer, self.location, self.subsite)
                
                if camgroup_conf is not None:
                    break
            except Exception as ex:
                console.error(f"Api is not up {ex}")
                time.sleep(10)
                continue
        if self.camera_group is not None and len(camgroup_conf) > 0:
            self.camera_group = self.camera_group + camgroup_conf
        elif self.camera_group is None and len(camgroup_conf) > 0:
            self.camera_group = camgroup_conf
        elif self.camera_group is None and len(camgroup_conf) == 0:
            self.camera_group = []
        else:
            self.camera_group = self.get_cam_group()

        
        preprocessconfig = {}
        secheduleconfig = {}
        # for dt in scheduledata:
        

        jsonreq = {"camera_group_id": self.camera_group}
        
        #tempschedule, _ = self.schedule.persist_data(jsonreq)

        # while True:
        tempschedule,tempdict,postprocessconfig,boundaryconfig=None,None,None,None
        
            
        tempschedule, _ = self.schedule.persist_data()

                
        
        tempdict = self.preprocs.persist_data(jsonreq)
                
        
        postprocessconfig = self.postprocess.persist_data()
                
        
        boundaryconfig = self.boundary.persist_data()
                
        

        

        preprocessconfig = tempdict
        secheduleconfig = tempschedule
        # if len(secheduleconfig)==0:
        #     secheduleconfig=tempschedule
        # else:
        #     secheduleconfig.update(secheduleconfig)

        # postprocessconfig = self.postprocess.persist_data()
        console.info("Persistingd data")

        boundaryconfig = self.boundary.persist_data()
        self.r.set("postprocess", json.dumps(postprocessconfig))
        
        self.r.set("scheduling", json.dumps(secheduleconfig))
        

        self.r.set("preprocess", json.dumps(preprocessconfig))

        self.r.set("boundary", json.dumps(boundaryconfig))
        
        

    def checkEvents(self,kafka,topic):
        """
        Continuously checking the kafka for config update, once it gets the event it will update the cache
        """
        self.persist_data()
        console.success("Caching started and updated")
        
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=kafka,
            auto_offset_reset="latest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="preprocess_cache",
        )
        for message in consumer:
            if message is None:
                continue
            else:
                
                messae_item = message.value
                items = [messae_item["item"]]
                
                self.persist_data()
                # print(items)
                # print("updated at===>", datetime.now())
                console.success("Preprocess cache updated at {0}".format(datetime.now()))
                
                # if len(set(items).intersection(set(["camera-group","camera","online-input","schedule",
                # "template","boundary-group","class","computation","incident","model",
                # "post-process","pre-process","usecase"])))>0:
                #     self.persist_data()
                # print("=======cache update=====")
