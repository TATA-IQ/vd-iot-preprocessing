from caching.rediscaching import Caching
from src.parser import Config
import requests

path = "config/config.yaml"
configdata = Config.yamlconfig(path)
print(configdata)
camera_group=[]
customer=[]
location=[]
subsite=[]

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

dbconf,preprocessconf,kafkaconf,consulconf=get_confdata(configdata)
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
