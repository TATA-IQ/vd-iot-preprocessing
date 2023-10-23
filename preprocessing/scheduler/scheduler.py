"""
Scheduler
"""

import json
import time
from datetime import datetime

import numpy as np
# from groups import CameraGroup
import redis



class Scheduler:
    """
    Uses Cache to Schedule Camera Group Events
    """

    def __init__(self):
        # self.url=url
        """
        Initialize the redis connection
        """
        pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
        self.r = redis.Redis(connection_pool=pool)
        self.daydict = {
            0: "monday",
            1: "tuesday",
            2: "wednesday",
            3: "thursday",
            4: "friday",
            5: "saturday",
            6: "sunday",
        }
        self.scheduledata = []
        self.schedulestatus = {}

    def daily(self, data):
        """
        Check for daily scheduling
        Args:
            data (dict): schedule dict of camera
        returns:
            data (dict): updated dictionry based on the daily schedule

        """
        print("***************")
        print(data)
        print("%%%%%%%%%%%%%%")
        try:
            scheduledtime = data["recurring_schedule"]
            start_time_str = scheduledtime["starttime"]
            end_time_str = scheduledtime["endtime"]
            start_time_arr = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"), start_time_str))
            end_time_arr = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"), end_time_str))
            currenttime = datetime.utcnow()
            start_time_seconds = [(currenttime - x).total_seconds() for x in start_time_arr]
            end_time_seconds = [(currenttime - x).total_seconds() for x in end_time_arr]
            start_status = np.any(np.array(start_time_seconds) > 0)
            end_status = np.any(np.array(end_time_seconds) < 0)
            print(start_time_seconds)
            print(end_time_seconds)
            print("===start status===", start_status)
            print("===end status===", end_status)
            if start_status and end_status:
                print("))))")
                data["current_state"] = True
            else:
                print("((((()))))")
                data["current_state"] = False
        except KeyError as ex:
            print("Exception in Daily Schedule ", ex)
            data["current_state"] = False
        print(data)
        return data

    def monthly(self, data):
        """
        Check for daily scheduling
        Args:
            data (dict): schedule dict of camera
        returns:
            data (dict): updated dictionry based on the monthly schedule

        """
        try:
            scheduledtime = data["monthly_schedule"]
            start_time_str = scheduledtime["starttime"]
            end_time_str = scheduledtime["endtime"]
            start_time_arr = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"), start_time_str))
            end_time_arr = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"), end_time_str))
            currenttime = datetime.utcnow()
            start_time_seconds = [(currenttime - x).total_seconds() for x in start_time_arr]
            end_time_seconds = [(currenttime - x).total_seconds() for x in end_time_arr]
            start_status = np.any(np.array(start_time_seconds) > 0)
            end_status = np.any(np.array(end_time_seconds) < 0)
            date = int(scheduledtime["date"])
            todaydate = datetime.utcnow().day

            print("===start status===", start_status)
            print("===end status===", end_status)

            if start_status and end_status and todaydate == date:
                data["current_state"] = True
            else:
                data["current_state"] = False
        except KeyError as ex:
            print("Exception in monthly Schedule ", ex)
            data["current_state"] = False
        return data

    def weekly(self, data):
        """
        Check for daily scheduling
        Args:
            data (dict): schedule dict of camera
        returns:
            data (dict): updated dictionry based on the Weekly schedule

        """
        try:
            scheduledtime = data["weekly_schedule"]
            start_time_str = scheduledtime["starttime"]
            end_time_str = scheduledtime["endtime"]
            start_time_arr = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"), start_time_str))
            end_time_arr = list(map(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"), end_time_str))
            currenttime = datetime.utcnow()
            start_time_seconds = [(currenttime - x).total_seconds() for x in start_time_arr]
            end_time_seconds = [(currenttime - x).total_seconds() for x in end_time_arr]
            start_status = np.any(start_time_seconds > 0)
            day = scheduledtime["weekday"].strip().lower()
            todayday = datetime.utcnow().today().weekday()

            end_status = np.any(np.array(end_time_seconds) < 0)
            print("===start status===", start_status)
            print("===end status===", end_status)

            if start_status and end_status and self.daydict[todayday] == day:
                data["current_state"] = True
            else:
                data["current_state"] = False
        except KeyError as ex:
            print("Exception in Weekly Schedule ", ex)
            data["current_state"] = False
        return data

    def onetime(self, data):
        """
        Check for daily scheduling
        Args:
            data (dict): schedule dict of camera
        returns:
            data (dict): updated dictionry based on the daily schedule

        """
        current_time = datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
        start_time_dt = datetime.strptime(data["starttime"], "%Y-%m-%d %H:%M:%S")
        end_time_dt = datetime.strptime(data["endtime"], "%Y-%m-%d %H:%M:%S")
        if start_time_dt >= current_time and current_time <= end_time_dt:
            data["current_state"] = True
        else:
            data["current_state"] = False

        return data

    def state_change(self):
        """
        Continuously Monitor for changes in the Cache.
        """
        count = 0
        while True:
            data = json.loads(self.r.get("scheduling"))
            print("&&&&&&&&")
            print(data)
            for dt in data:
                print("======")
                print(dt)
                print("******")
                frequency = data[dt]["frequency_type_id"]
                if int(frequency) == 1:
                    data[dt] = self.monthly(data[dt])
                if frequency == 2:
                    data[dt] = self.weekly(data[dt])
                if frequency == 3:
                    data[dt] = self.daily(data[dt])
                if frequency == 4:
                    data[dt] = self.daily(data[dt])
            self.r.set("scheduling", json.dumps(data))
            print("Runned at====>", datetime.now().strftime("%y-%d-%m %H:%M%S"))
            print("======Run count=====", count)
            count = count + 1
            time.sleep(30)


sc = Scheduler()
sc.state_change()
