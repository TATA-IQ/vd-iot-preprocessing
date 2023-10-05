import requests
class PersistSchedule():
    """
    This Class fetch all the data related to scheduling
    """

    def __init__(self, url="http://127.0.0.1:8000/getScheduleMaster"):
        self.url = url
        self.scheduledata = None

    def apiCall(self, data: dict = None) -> list:
        """
        Call the api for camera config
        Args:
            data: request query
        returns:
            list: detail  data of requested query
        """
        cameraconfdata = []
        if data is None:
            print("None")
            resposnse = requests.get(self.url, json={}, timeout=50)
        else:
            resposnse = requests.get(self.url, json=data, timeout=50)
            #sts.get(self.url, json=data, timeout=50)
        # print(resposnse)
        # print(resposnse.json())
        scheduledata=None
        if resposnse.status_code == 200:
            scheduledata = resposnse.json()["data"]
        return scheduledata


    def persistData(self,jsonreq={}):
        
        data= self.apiCall(jsonreq)
        dictres = {}

        dictres["scheduling"] = {}
        tempdict = {}
        for dt in data:
            dt["current_state"] = True
            tempdict[dt["schedule_id"]] = dt
        dictres["scheduling"] = tempdict
        
        return tempdict, data