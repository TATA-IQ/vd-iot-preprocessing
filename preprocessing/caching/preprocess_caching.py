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
                print("None")
                resposnse = requests.get(self.url, json={}, timeout=50)
            else:
                resposnse = requests.get(self.url, json=data, timeout=50)
            # print(resposnse)
            # print(resposnse.json())
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
        print("data====>", data)
        preprocessconf = self.api_call(data=data)
        # print(preprocessconf)
        preprocess_config_dict = {}
        # brightness = []
        # contrast_alpha = []
        # contrast_beta = []
        # mask_image = []
        # split = []
        # split_columns = []
        # split_rows = []
        # threshold = []
        # preprocess_name = []
        # preprocess_type = []
        # scheduling_id = []
        # usecase_id = []
        # uscase_name = []

        for dt in preprocessconf:
            # dt["schedule_id"] = scheduledata["schedule_id"]
            print(dt)
            if dt["camera_id"] not in preprocess_config_dict.keys():
                print("===>if")
                preprocess_config_dict[dt["camera_id"]] = {}

                preprocess_config_dict[dt["camera_id"]][dt["usecase_id"]] = dt
            else:
                preprocess_config_dict[dt["camera_id"]][dt["usecase_id"]] = dt
                print("else*********")

                # preprocess_config_dict[dt["camera_id"]["camera_grouplist_id"]]=dt["camera_grouplist_id"]
                # preprocess_config_dict[dt["camera_id"]["camera_group_id"]]=dt["camera_group_id"]
                # preprocess_config_dict[dt["camera_id"]["pre_config_id"]]=dt["pre_config_id"]
                # preprocess_config_dict[dt["camera_id"]["preprocess_id"]]=dt["preprocess_id"]
                # preprocess_config_dict[dt["camera_id"]["brightness"]]=dt["brightness"]
                # preprocess_config_dict[dt["camera_id"]["contrast_alpha"]]=dt["contrast_alpha"]
                # preprocess_config_dict[dt["camera_id"]["contrast_beta"]]=dt["contrast_beta"]
                # preprocess_config_dict[dt["camera_id"]["mask_image"]]=dt["mask_image"]
                # preprocess_config_dict[dt["camera_id"]["split"]]=dt["split"]
                # preprocess_config_dict[dt["camera_id"]["split_columns"]]=dt["split_columns"]
                # preprocess_config_dict[dt["camera_id"]["split_rows"]]=dt["split_rows"]
                # preprocess_config_dict[dt["camera_id"]["threshold"]]=dt["threshold"]

            # else:
            #     pass

            # else:
            #     preprocess_config_dict[dt["camera_group_id"]].append(dt)
            # print("******")
            # print(preprocess_config_dict)

        return preprocess_config_dict
