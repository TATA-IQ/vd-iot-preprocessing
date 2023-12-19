"""
PreProcess Configuration
"""
import requests


class PersistPreprocessConfig:
    """
    This class fetch camera config details from rest api
    Caching is on level {"camera_id":{"usecase_id":data}}
    """

    def __init__(self, url="http://127.0.0.1:8000/getPreprocessConfig"):
        """
        Saving Preprocessing To Cache
        Args:
            url (str): url of preprocess configuration api
        """
        self.url = url

    def api_call(self, data: dict = None) -> list:
        """
        Call the api for camera config
        Args:
            data (json or dict): request query
        returns:
            responsedata (list): detail  data of requested query
        """
        responsedata = []
        try:
            if data is None:
                
                resposnse = requests.get(self.url, json={}, timeout=50)
            else:
                resposnse = requests.get(self.url, json=data, timeout=50)
            
            if resposnse.status_code == 200:
                responsedata = resposnse.json()["data"]
        except Exception as ex:
            print("Exception while preprocess caching: ",ex)
        return responsedata

    def persist_data(self, data):
        """
        Call the api for camera config
        Args:
            data (json or dict): request query
        returns:
            preprocess_config_dict (dict): detail  data of preprocessing configuration
        """
        
        preprocessconf = self.api_call(data=data)
        
        preprocess_config_dict = {}
        
        for dt in preprocessconf:
            # dt["schedule_id"] = scheduledata["schedule_id"]
            
            if dt["camera_id"] not in preprocess_config_dict.keys():
                
                preprocess_config_dict[dt["camera_id"]] = {}

                preprocess_config_dict[dt["camera_id"]][dt["usecase_id"]] = dt
            else:
                preprocess_config_dict[dt["camera_id"]][dt["usecase_id"]] = dt
                

                
            
        return preprocess_config_dict
