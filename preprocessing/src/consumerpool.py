import json
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Manager, Queue

import redis
from shared_memory_dict import SharedMemoryDict
from src.consumer import RawImageConsumer
from console_logging.console import Console
console=Console()
# os.environ["SHARED_MEMORY_USE_LOCK"]="1"
manager = Manager()
queudict = {}
preprocess_smd = manager.dict()
# queue_config=Queue()
postprocess_smd = SharedMemoryDict(name="postprocess", size=10000000)
preprocess_smd = SharedMemoryDict(name="preprocess", size=10000000)
boundary_smd = SharedMemoryDict(name="boundary", size=10000000)





def testcallbackFuture(future):
    console.error(" Future error cameragroup {0}".format(future.exception()))


def testFuture(obj,postprocss_api):
    
    obj.connectConsumer(postprocss_api)

    
    # queudict[cam_id]=q
    console.info("====Process submitted===")

    thread_executor_list=obj.multiple_consumer()
    while True:
        for i in thread_executor_list:
        
            if not i.running():
                
                break

    


class PoolConsumer:
    def __init__(self, kafkahost, redis_server, postprocess_api,logger):
        """
        Initialize the  Camera Group and connect with redis to take the recent configuration
        """
        self.kafkahost = kafkahost
        pool = redis.ConnectionPool(host=redis_server["host"], port=redis_server["port"], db=0)
        self.r = redis.Redis(connection_pool=pool)
        self.dict3 = {}
        self.postprocss_api=postprocess_api
        self.logger = logger
        # self.smd = SharedMemoryDict(name='tokens', size=1024)

    def startFuture(self, obj):
        
        obj.connectConsumer()
        
        return 1

    def getScheduleState(self, scheduledata, camdata):
        """
        Get the current state of scheduling for each use case and camera
        Args:
            scheduledata
            camdata
        Returns:
            camdata
        """
        usecase = list(camdata.keys())
        # print(camdata)
        for i in usecase:
            schedule_id = camdata[i]["scheduling_id"]
            # print("=====>scheule===>",camdata[i])
            camdata[i]["current_state"] = scheduledata[str(schedule_id)]["current_state"]
        return camdata
    def remove_topic(self, camlist, futuredict):
        camlist = list(map(lambda x: int(x), camlist))
        return list(set(futuredict.keys()) - set(camlist))

    def checkState(self):
        """
        Always updates the data from the caching
        For ex: If any camera is added in group, it will check the group and start new process for camera or remove camera if
        camera is delated from the group
        """

        manager = Manager()
        statusdict = manager.dict()
        futuredict = {}
        
        executor = ProcessPoolExecutor(100)
        console.info("Starting preprocessing")
        while True:
            try:
                
                scheduledata = json.loads(self.r.get("scheduling"))

                camdata = json.loads(self.r.get("preprocess"))
                postprocessconfig = json.loads(self.r.get("postprocess"))
                boundaryconfig = json.loads(self.r.get("boundary"))
            except Exception as ex:
                self.logger.error("Exception While loading cache {0}".format(ex))
                console.error("Exception While loading cache {0}".format(ex))
                continue
            for ki in postprocessconfig:
                postprocess_smd[str(ki)] = postprocessconfig[ki]
            for ki in boundaryconfig:
                boundary_smd[str(ki)] = boundaryconfig[ki]
            camtoremove = self.remove_topic(camdata.keys(), futuredict)
            self.logger.info(f" These Cam Have been Removed From Group {camtoremove}")
            
            for cam in camtoremove:
                try:
                    futuredict[cam].cancel()
                except Exception as ex:
                    self.logger.info("Exception while removing cam ",ex)
                    console.error(f"Exception while removing cam {ex}")

                del futuredict[cam]
                del statusdict[cam]
                self.logger.info(f"Killing camera {cam}")
                console.info(f"Killing camera {cam}")

            for cam in camdata.keys():
                usecasekeys = list(camdata[cam].keys())
                
                tempcam = camdata[cam][usecasekeys[0]]
                cam_id = tempcam["camera_id"]
                camera_group_id = tempcam["camera_group_id"]
                #if cam_id < 50:
                if cam_id not in statusdict:
                    preproceesdata = self.getScheduleState(scheduledata, camdata[cam])
                    
                    preprocess_smd[str(cam_id)] = preproceesdata
                    obj = RawImageConsumer(self.kafkahost, cam_id, self.logger)
                    statusdict[cam_id] = obj
                    
                    future1 = executor.submit(testFuture, obj, self.postprocss_api)
                    future1.add_done_callback(testcallbackFuture)
                    futuredict[cam_id] = future1
                    self.logger.info(f"Starting Conusmer for {cam_id}")
                    console.info(f"Starting Conusmer for {cam_id}")

                else:
                    preproceesdata = self.getScheduleState(scheduledata, camdata[cam])
                    preprocess_smd[str(cam_id)] = preproceesdata
                    self.logger.info(f"Updating Data for {cam_id}")
                    # console.info(f"Updating Data for {cam_id}")
                    
                    if not futuredict[cam_id].running():
                        futuredict[cam_id].cancel()
                        preproceesdata = self.getScheduleState(scheduledata, camdata[cam])
                        preprocess_smd[str(cam_id)] = preproceesdata
                        obj = RawImageConsumer(self.kafkahost, cam_id, self.logger)
                        statusdict[cam_id] = obj

                        future1 = executor.submit(testFuture, obj, self.postprocss_api)
                        futuredict[cam_id] = future1
                        self.logger.info(f"Starting New Conusmer for {cam_id}")
                    
            time.sleep(2)
            
