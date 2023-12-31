from caching.rediscaching import Caching
from src.parser import Config
import requests
import consul

path = "config/config.yaml"
configdata = Config.yamlconfig(path)
print(configdata)
camera_group=[]
customer=[]
location=[]
subsite=[]

def get_service_address(consul_client,service_name,env):
    while True:
        
        try:
            services=consul_client.catalog.service(service_name)[1]
            print(services)
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

    
    
    print("======dbres======")
    print(dbres)
    print(preprocessconf)
    #postprocessapi="http://"+pphost+":"+str(ppport)+preprocessconf["postprocess"]
    return  dbres,preprocessconf,kafkaconf

dbconf,preprocessconf,kafkaconf=get_confdata(configdata[0]["consul"])
api = dbconf["apis"]
kafka=kafkaconf["kafka"]
topic=preprocessconf["event_topic"]
redis=preprocessconf["redis"]
print("===========>",api)

if preprocessconf["read_config"]:
    try:
        customer = preprocessconf["config"]["customer"]
    except RuntimeWarning as ex:
        print("Customer Ids Not found: ", ex)
        customer = None
    try:
        subsite = preprocessconf["config"]["subsite"]
    except RuntimeWarning as ex:
        print("Subsite Ids Not Found: ", ex)
        subsite = None
    try:
        location = preprocessconf["config"]["location"]
    except RuntimeWarning as ex:
        print("Location not found: ", ex)
        location = None
    try:
        camera_group = preprocessconf["config"]["group"]
    except RuntimeWarning as ex:
        print("Camera Group Not Found: ", ex)
        camera_group = []

if __name__ == "__main__":
    '''
    Start Preprocess Caching
    '''
    cs = Caching(api,redis, camera_group, customer, location, subsite)
    #cs.persist_data()
    cs.checkEvents(kafka, topic)
