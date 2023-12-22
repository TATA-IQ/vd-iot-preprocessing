"""
Code to start PreProcessing and Cosnumers
"""
import os
import requests
import consul
import time
from shared_memory_dict import SharedMemoryDict
from sourcelogs.logger import create_rotating_log
from src.consumerpool import PoolConsumer
from src.parser import Config
from console_logging.console import Console
console=Console()
os.environ["SHARED_MEMORY_USE_LOCK"] = "1"

def get_service_address(consul_client,service_name,env):
    while True:
        
        try:
            services=consul_client.catalog.service(service_name)[1]
            console.info(f" Service Extracted from Cosnul For {0} : {1}".format(service_name,services))
            for i in services:
                if env == i["ServiceID"].split("-")[-1]:
                    return i
        except:
            time.sleep(10)
            continue
def get_confdata(consul_conf):
    consul_client = consul.Consul(host=consul_conf["host"],port=consul_conf["port"])
    pipelineconf=get_service_address(consul_client,"pipelineconfig",consul_conf["env"])

    
    
    env=consul_conf["env"]
    
    endpoint_addr="http://"+pipelineconf["ServiceAddress"]+":"+str(pipelineconf["ServicePort"])
    print("endpoint addr====",endpoint_addr)
    while True:
        
        try:
            res=requests.get(endpoint_addr+"/")
            endpoints=res.json()
            print("===got endpoints===",endpoints)
            break
        except Exception as ex:
            print("endpoint exception==>",ex)
            time.sleep(10)
            continue
    
    while True:
        try:
            res=requests.get(endpoint_addr+endpoints["endpoint"]["preprocess"])
            preprocessconf=res.json()
            print("preprocessconf===>",preprocessconf)
            break
            

        except Exception as ex:
            print("preprocessconf exception==>",ex)
            time.sleep(10)
            continue
    while True:
        try:
            res=requests.get(endpoint_addr+endpoints["endpoint"]["kafka"])
            kafkaconf=res.json()
            print("kafkaconf===>",kafkaconf)
            break
            

        except Exception as ex:
            print("kafkaconf exception==>",ex)
            time.sleep(10)
            continue
    print("=======searching for dbapi====")
    while True:
        try:
            print("=====consul search====")
            dbconf=get_service_address(consul_client,"dbapi",consul_conf["env"])
            print("****",dbconf)
            dbhost=dbconf["ServiceAddress"]
            dbport=dbconf["ServicePort"]
            res=requests.get(endpoint_addr+endpoints["endpoint"]["dbapi"])
            dbres=res.json()
            print("===got db conf===")
            print(dbres)
            break
        except Exception as ex:
            print("db discovery exception===",ex)
            time.sleep(10)
            continue
    for i in dbres["apis"]:
        print("====>",i)
        dbres["apis"][i]="http://"+dbhost+":"+str(dbport)+dbres["apis"][i]

    while True:
        try:
            print("=====consul search====")
            ppconf=get_service_address(consul_client,"postprocess",consul_conf["env"])
            print("****",dbconf)
            pphost=ppconf["ServiceAddress"]
            ppport=ppconf["ServicePort"]
            
            break
        except Exception as ex:
            print("db discovery exception===",ex)
            time.sleep(10)
            continue
    
    print("======dbres======")
    print(dbres)
    print(preprocessconf)
    postprocessapi="http://"+pphost+":"+str(ppport)+preprocessconf["postprocess"]
    return  dbres,preprocessconf,kafkaconf,postprocessapi


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
        dbconf,preprocessconf,kafkaconf,postprocessapi=get_confdata(conf[0]["consul"])
        redis_server=preprocessconf["redis"]
        postprocess_api=postprocessapi
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
