"""
Scheduler Configuration Caching
"""
import requests


class PersistSchedule:
    """
    This Class fetch all the data related to scheduling
    """

    def __init__(self, url):
        """
        Saving scheduling to cache
        Args:
            url (str): schedule rest api url
        """
        self.url = url
        self.scheduledata = None

    def apiCall(self, query: dict = None) -> list:
        """
        Call the api for camera config
        Args:
            query (dict or json): request query
        returns:
            scheduledata (list): detail  data of requested query
        """
        cameraconfdata = []
        if query is None:
            print("None")
            response_schedule = requests.get(self.url, json={}, timeout=50)
        else:
            response_schedule = requests.get(self.url, json=query, timeout=50)
            # sts.get(self.url, json=data, timeout=50)
        # print(resposnse)
        # print(resposnse.json())
        scheduledata = None
        if response_schedule.status_code == 200:
            scheduledata = response_schedule.json()["data"]
        return scheduledata

    def persist_data(self, jsonreq={}):
        """
        Prepare scheduling configuration and send it to rediscaching module to save the data
        returns:
            schedule_config (dict): schedule configuration dict

        """
        data = self.apiCall(jsonreq)
        dictres = {}

        dictres["scheduling"] = {}
        schedule_config = {}
        for dt in data:
            dt["current_state"] = True
            schedule_config[dt["schedule_id"]] = dt
        dictres["scheduling"] = schedule_config

        return schedule_config, data
