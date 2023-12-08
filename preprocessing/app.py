"""
Code to start PreProcessing and Cosnumers
"""
import os
import requests
import consul
from shared_memory_dict import SharedMemoryDict
from sourcelogs.logger import create_rotating_log
from src.consumerpool import PoolConsumer
from src.parser import Config

os.environ["SHARED_MEMORY_USE_LOCK"] = "1"

def get_confdata(conf):
    res=requests.get(conf[0]["consul_url"])
    data=res.json()
    dbconf =None
    
    preprocessconf=None
    env=None
    consulconf=None
    if "pipelineconfig" in data:
        port=data["pipelineconfig"]["Port"]
        while True:
            endpoints=requests.get("http://pipelineconfig.service.consul:"+str(port)+"/").json()
            #print(endpoints)
            if "preprocess" in endpoints["endpoint"]:
                try:
                    preprocessconf=requests.get("http://pipelineconfig.service.consul:"+str(port)+"/"+endpoints["endpoint"]["preprocess"]).json()
                except Exception as ex:
                    print(ex)
                    time.sleep(5)
                    continue
            if "dbapi" in endpoints["endpoint"] and "dbapi" in data:
                try:
                    dbconf=requests.get("http://pipelineconfig.service.consul:"+str(port)+"/"+endpoints["endpoint"]["dbapi"]).json()
                except Exception as ex:
                    print(ex)
                    time.sleep(5)
                    continue
            
            if "kafka" in endpoints["endpoint"]:
                try:
                    kafkaconf=requests.get("http://pipelineconfig.service.consul:"+str(port)+"/"+endpoints["endpoint"]["kafka"]).json()
                except Exception as ex:
                    print(ex)
                    time.sleep(5)
                    continue
            if "consul" in endpoints["endpoint"]:
                try:
                    consulconf=requests.get("http://pipelineconfig.service.consul:"+str(port)+"/"+endpoints["endpoint"]["consul"]).json()
                except Exception as ex:
                    print(ex)
                    time.sleep(5)
                    continue
            print(dbconf)
            print(preprocessconf)
            if dbconf is not None and preprocessconf is not None and kafkaconf is not None:
                break
    print("******")
    print(dbconf)
    return  dbconf,preprocessconf,kafkaconf,consulconf

preprocess_smd = SharedMemoryDict(name="preprocess", size=10000000)
postprocess_smd = SharedMemoryDict(name="postprocess", size=10000000)
boundary_smd = SharedMemoryDict(name="boundary", size=10000000)
if __name__ == "__main__":
    '''
    Start Preprocessing Module
    '''
    try:
        preprocess_smd.shm.close()
        preprocess_smd.shm.unlink()
        postprocess_smd.shm.close()
        postprocess_smd.shm.unlink()
        boundary_smd.shm.close()
        boundary_smd.shm.unlink()
        del preprocess_smd
        del postprocess_smd
        del boundary_smd
        conf = Config.yamlconfig("config/config.yaml")
        dbconf,preprocessconf,kafkaconf,consulconf=get_confdata(conf)
        redis_server=preprocessconf["redis"]
        postprocess_api=dbconf["postprocessing_api"]["api"]
        # print(data[0]["kafka"])
        logg = create_rotating_log("logs/logs.log")
        cg = PoolConsumer(kafkaconf["kafka"], redis_server,postprocess_api ,logg)
        cg.checkState()
    except KeyboardInterrupt:
        print("=====Removing Shared Memory Refrence=====")
        preprocess_smd.shm.close()
        preprocess_smd.shm.unlink()
        postprocess_smd.shm.close()
        postprocess_smd.shm.unlink()
        boundary_smd.shm.close()
        boundary_smd.shm.unlink()
        del preprocess_smd
        del postprocess_smd
        del boundary_smd
