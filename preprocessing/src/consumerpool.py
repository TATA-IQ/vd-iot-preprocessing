import json
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager, Queue

import redis
from shared_memory_dict import SharedMemoryDict
from src.consumer import RawImageConsumer

# os.environ["SHARED_MEMORY_USE_LOCK"]="1"
manager = Manager()
queudict = {}
preprocess_smd = manager.dict()
# queue_config=Queue()
postprocess_smd = SharedMemoryDict(name="postprocess", size=10000000)
preprocess_smd = SharedMemoryDict(name="preprocess", size=10000000)
boundary_smd = SharedMemoryDict(name="boundary", size=10000000)


text = "pqr"


def testcallbackFuture(future):
    print("=======callback future====", future.exception())


def testFuture(obj):
    obj.connectConsumer()

    
    # queudict[cam_id]=q
    obj.runConsumer()

    # obj.callConsumer()


class PoolConsumer:
    def __init__(self, kafkahost, logger):
        """
        Initialize the  Camera Group and connect with redis to take the recent configuration
        """
        self.kafkahost = kafkahost
        pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
        self.r = redis.Redis(connection_pool=pool)
        self.dict3 = {}
        self.log = logger
        # self.smd = SharedMemoryDict(name='tokens', size=1024)

    def startFuture(self, obj):
        print("Future")
        obj.connectConsumer()
        # obj.startConsumer()
        # obj.messageParse()

        # while obj.isConnected():
        #     a=a+1
        # while True:
        #     a=a+1
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

    def checkState(self):
        """
        Always updates the data from the caching
        For ex: If any camera is added in group, it will check the group and start new process for camera or remove camera if
        camera is delated from the group
        """

        manager = Manager()
        statusdict = manager.dict()
        futuredict = {}
        # queudict={}
        # statusdict={}
        executor = ProcessPoolExecutor(10)
        while True:
            scheduledata = json.loads(self.r.get("scheduling"))
            camdata = json.loads(self.r.get("preprocess"))
            postprocessconfig = json.loads(self.r.get("postprocess"))
            boundaryconfig = json.loads(self.r.get("boundary"))
            # print("*********",scheduledata)
            for ki in postprocessconfig:
                postprocess_smd[str(ki)] = postprocessconfig[ki]
            for ki in boundaryconfig:
                boundary_smd[str(ki)] = boundaryconfig[ki]
            # print("===========+++++++=======")
            # print(postprocess_smd)
            for cam in camdata.keys():
                usecasekeys = list(camdata[cam].keys())
                # print("#####",camdata[cam])
                # print(camdata)
                # self.usecaseids=list(self.cachedata[str(cameraid)].keys())
                # topic = camdata[cam][str(usecasekeys[0])]["topic_name"]
                tempcam = camdata[cam][usecasekeys[0]]
                cam_id = tempcam["camera_id"]
                camera_group_id = tempcam["camera_group_id"]
                if cam_id < 50:
                    if cam_id not in statusdict:
                        preproceesdata = self.getScheduleState(scheduledata, camdata[cam])
                        # print("*********",preproceesdata)
                        preprocess_smd[str(cam_id)] = preproceesdata
                        obj = RawImageConsumer(self.kafkahost, cam_id, self.log)
                        statusdict[cam_id] = obj
                        # queudict[cam_id]=Queue()
                        print("Starting consumer====", cam_id)
                        future1 = executor.submit(testFuture, obj)
                        # executor.submit(,"dddf")
                        future1.add_done_callback(testcallbackFuture)
                        # listapp.append(future1)
                        futuredict[cam_id] = future1
                        self.log.info(f"Starting Conusmer for {cam_id}")

                    else:
                        # statusdict[cam_id].update("abc")
                        # print("=====else===",cam_id)
                        # print(futuredict[cam_id].done())
                        # print(futuredict[cam_id].running())
                        # #print("=====else===",cam_id)
                        preproceesdata = self.getScheduleState(scheduledata, camdata[cam])
                        preprocess_smd[str(cam_id)] = preproceesdata
                        self.log.info(f"Updating Data for {cam_id}", preproceesdata)
                        # print(preprocess_smd)
                        print("========Updating by Update=====")
                        # print(preprocess_smd[str(cam_id)])
                        # executor.submit(statusdict[cam_id].update,"updated by parent")
                        # print("*"*100)
                        # queudict[cam_id].put(preprocess_smd)

                        if not futuredict[cam_id].running():
                            futuredict[cam_id].cancel()
                            preproceesdata = self.getScheduleState(scheduledata, camdata[cam])
                            preprocess_smd[str(cam_id)] = preproceesdata
                            # preprocess_smd[cam_id]=camdata[cam]
                            # print(preprocess_smd)
                            obj = RawImageConsumer(self.kafkahost, cam_id, self.log)
                            statusdict[cam_id] = obj

                            future1 = executor.submit(testFuture)
                            # listapp.append(future1)
                            futuredict[cam_id] = future1
                            self.log.info(f"Starting New Conusmer for {cam_id}")
                        # else:
                        # print("Updating===>",cam_id)

                    time.sleep(3)
            # print(statusdict)
            time.sleep(5)
            # print("preprocess_smd===>",postprocess_smd)
