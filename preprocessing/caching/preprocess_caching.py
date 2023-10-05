import requests

class PersistPreprocessConfig():
    """
    This class fetch camera config details from rest api
    Caching is on level {"camera_id":{"usecase_id":data}}
    """

    def __init__(self, url="http://127.0.0.1:8000/getPreprocessConfig"):
        self.url = url

    def apiCall(self, data: dict = None) -> list:
        """
        Call the api for camera config
        Args:
            data: request query
        returns:
            list: detail  data of requested query
        """
        responsedata = []
        if data is None:
            print("None")
            resposnse = requests.get(self.url, json={}, timeout=50)
        else:
            resposnse = requests.get(self.url, json=data, timeout=50)
        # print(resposnse)
        # print(resposnse.json())
        if resposnse.status_code == 200:
            responsedata = resposnse.json()["data"]
        return responsedata


    def persistData(self, data):
        print("data====>",data)
        preprocessconf = self.apiCall(data=data)
        #print(preprocessconf)
        tempdict = {}
        brightness=[]
        contrast_alpha=[]
        contrast_beta=[]
        mask_image=[]
        split=[]
        split_columns=[]
        split_rows=[]
        threshold=[]
        preprocess_name=[]
        preprocess_type=[]
        scheduling_id=[]
        usecase_id=[]
        uscase_name=[]
         
        for dt in preprocessconf:
            #dt["schedule_id"] = scheduledata["schedule_id"]
            print(dt)
            if dt["camera_id"] not in tempdict.keys():
                print("===>if")
                tempdict[dt["camera_id"]] = {}

                tempdict[dt["camera_id"]][dt["usecase_id"]]=dt
            else:
                tempdict[dt["camera_id"]][dt["usecase_id"]]=dt
                print("else*********")

                # tempdict[dt["camera_id"]["camera_grouplist_id"]]=dt["camera_grouplist_id"]
                # tempdict[dt["camera_id"]["camera_group_id"]]=dt["camera_group_id"]
                # tempdict[dt["camera_id"]["pre_config_id"]]=dt["pre_config_id"]
                # tempdict[dt["camera_id"]["preprocess_id"]]=dt["preprocess_id"]
                # tempdict[dt["camera_id"]["brightness"]]=dt["brightness"]
                # tempdict[dt["camera_id"]["contrast_alpha"]]=dt["contrast_alpha"]
                # tempdict[dt["camera_id"]["contrast_beta"]]=dt["contrast_beta"]
                # tempdict[dt["camera_id"]["mask_image"]]=dt["mask_image"]
                # tempdict[dt["camera_id"]["split"]]=dt["split"]
                # tempdict[dt["camera_id"]["split_columns"]]=dt["split_columns"]
                # tempdict[dt["camera_id"]["split_rows"]]=dt["split_rows"]
                # tempdict[dt["camera_id"]["threshold"]]=dt["threshold"]
                




            # else:
            #     pass

            # else:
            #     tempdict[dt["camera_group_id"]].append(dt)
            #print("******")
            #print(tempdict)

        return tempdict
