import redis
import requests
import json
import threading
from kafka import KafkaConsumer
from caching.postprocess_caching import *
from caching.schedule_caching import *
from caching.preprocess_caching import *
from caching.boundary_caching import *

class Caching:
    """
    This class handles the caching of the respective module
    And always listens for the event changes in kafka.
    If any event is encountered it will update the caching.
    """
    

    def __init__(
        self,
        api: dict,
        camera_group: list = None,
        customer: list = None,
        location: list = None,
        subsite: list = None,  # noqa: E501
        zone: list=None   
    ) -> None:  # noqa: E501
        """
        Initialize the caching
        Args:
            api: dict of apis
            customer: list of customer id, by default is None
            location: list of customer id, by default is None
            subsite: list of subsite id, by default is None
            camera_group: list of camera group, by default is None
        """
        pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
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
        self.zone=zone
        self.schedule = PersistSchedule()
        self.preprocs = PersistPreprocessConfig()

        self.api = api
        self.postprocess=PersistPostProcessConfig(self.api)
        self.boundary=PersistBoundaryConfig(self.api)
        # self.urllist=urllist

    def getCamGroup(
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
            customer: list of customer id, by default is None
            location: list of customer id, by default is None
            subsite: list of subsite id, by default is None
            zone: list of zone id, by default is None
            camera_group: list of camera group, by default is None
        returns:
            list: All the cameragroup
        """
        camgroup = []
        if customer is None and location is None and subsite is None and camera_group is None and zone is None:  # noqa: E501
            r = requests.get(self.api["camera_group"], timeout=50)
            try:
                camgroup = r.json()["data"]
            except Exception as ex:
                print("Camgroup exception: ", ex)
                return []

        if customer is not None:
            r = requests.get(self.api["camera_group"], json={"customer_id": customer}, timeout=50)  # noqa: E501
            try:
                camgroup = r.json()["data"]
                # print("===customer==",camgroup)
            except Exception as ex:
                print("Exceptin while fetching customer ", ex)
                pass
        if location is not None:
            r = requests.get(self.api["camera_group"], json={"location_id": location}, timeout=50)  # noqa: E501
            try:
                if len(camgroup) > 0:
                    camgroup = camgroup + r.json()["data"]
                    print("===location==", camgroup)
            except Exception as ex:
                print("location data exception: ", ex)
                pass
        if subsite is not None:
            r = requests.get(self.api["camera_group"], json={"subsite_id": subsite}, timeout=50)  # noqa: E501
            try:
                if len(camgroup) > 0:
                    camgroup = camgroup + r.json()["data"]
                    print("===subsite==", camgroup)
            except Exception as ex:
                print("subsite data exception: ", ex)
                pass
        if zone is not None:
            r = requests.get(self.api["camera_group"], json={"zone_id": zone}, timeout=50)  # noqa: E501
            try:
                if len(camgroup) > 0:
                    camgroup = camgroup + r.json()["data"]
                    print("===Zone Id==", camgroup)
            except Exception as ex:
                print("Zone data exception: ", ex)
                pass

        return list(set(camgroup))

    def persistData(self):
        camgroup_conf= self.getCamGroup(self.customer,self.location,self.subsite)
        if self.camera_group is not None and len(camgroup_conf)>0:
            self.camera_group=self.camera_group+camgroup_conf
        elif self.camera_group is None and len(camgroup_conf)>0:
            self.camera_group=camgroup_conf
        elif self.camera_group is None and len(camgroup_conf)==0:
            self.camera_group=[]
        else:
            self.camera_group=self.getCamGroup()
        
        print("camera group---->",self.camera_group)
        #persistdata, scheduledata = self.schedule.persistData()
        #self.r.set("scheduling", json.dumps(persistdata))
        preprocessconfig = {}
        secheduleconfig={}
        #for dt in scheduledata:
        print("&&&&&&&&&&&&&&&",self.camera_group)
        
        jsonreq = {
            
            "camera_group_id": self.camera_group
        }
        tempschedule,_=self.schedule.persistData(jsonreq)
        tempdict= self.preprocs.persistData(jsonreq)

        preprocessconfig = tempdict
        secheduleconfig=tempschedule
        # if len(secheduleconfig)==0:
        #     secheduleconfig=tempschedule
        # else:
        #     secheduleconfig.update(secheduleconfig)
        
        postprocessconfig=self.postprocess.persistData()
        boundaryconfig=self.boundary.persistData()
        print("*****====>", len(preprocessconfig))
        self.r.set("scheduling", json.dumps(secheduleconfig))
        print("====boundary===")
        print(boundaryconfig)

        self.r.set("preprocess", json.dumps(preprocessconfig))
        self.r.set("postprocess", json.dumps(postprocessconfig))
        self.r.set("boundary", json.dumps(boundaryconfig))
        print(preprocessconfig.keys())

    def checkEvents(self):
        consumer = KafkaConsumer(
            "app_events",
            bootstrap_servers=[
                "172.16.0.175:9092",
                "172.16.0.171:9092",
                "172.16.0.174:9092",
            ],
            auto_offset_reset="latest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="preprocess_cache"
        )
        for message in consumer:
            if message is None:
                continue
            else:
                print("=======message=====")
                print(message)
                messae_item=message.value
                items=[messae_item["item"]]
                print(items)
                self.persistData()
                print(set(items).intersection(set(["camera-group","camera","online-input","schedule",
                "template","boundary-group","class","computation","incident","model",
                "post-process","pre-process","usecase"])))
                # if len(set(items).intersection(set(["camera-group","camera","online-input","schedule",
                # "template","boundary-group","class","computation","incident","model",
                # "post-process","pre-process","usecase"])))>0:
                #     self.persistData()
                    # print("=======cache update=====")



