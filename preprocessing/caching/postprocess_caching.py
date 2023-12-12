"""
Postrproces Configuration
"""
import requests


class PersistPostProcessConfig:
    def __init__(self, apis):
        """
        Saving Postprocessing To Cache
        Args:
            apis (list): list of apis
        """
        self.apis = apis

    def model_classes(self, usecase_id):
        """
        Fetch all the classes for usecase id along with model details
        Args:
            usecase_id (int or str): usecase id
        returns:
            modeldata (list): returns list of configured classes and model details
        """
        modeldata = self.api_call(self.apis["classes"], data={"usecase_id": usecase_id})
        # modeldata = classresponse.json()["data"]
        # print(modeldata)
        return modeldata

    def computation_data(self, usecase_id):
        """
        Fetch computation data for given usecase id
        Args:
            usecase_id (int or str): usecase id
        returns:
            computationdata (list): list of computation data for uswcase id
        """
        computationdata = self.api_call(self.apis["computation"], data={"usecase_id": usecase_id})
        # computationdata=computationresponse.json()["data"]
        # print(computationdata)
        return computationdata

    def get_usecase(self):
        """
        Get all the usecases
        """
        usecaseres = self.api_call(self.apis["usecase_urls"])
        if len(usecaseres) > 0:
            return usecaseres["usecase_id"]
        else:
            return []

    def api_call(self, url, data: dict = None) -> list:
        """
        Call the api for camera config
        Args:
            data (dict or json): request query
        returns:
            responsedata (list): detail  data of requested query
        """
        cameraconfdata = []
        responsedata = []
        print("*******data", data)
        try:
            if data is None:
                print("None")
                resposnse = requests.get(url, json={}, timeout=50)
            else:
                resposnse = requests.get(url, json=data, timeout=50)
            # print(resposnse)
            print(resposnse.json())
            print(url, data)
            if resposnse.status_code == 200:
                responsedata = resposnse.json()["data"]
                print(responsedata)
        except Exception as ex:
            print("Exception while calling postprocessing api")
        return responsedata

    def postprocess_master(self):
        """
        Get all the post processing configuration
        returns:
            postconfigdata (dict): all usecases post process configuration
        """
        postconfigdata = {}
        postconf_data = []
        usecaseid = self.get_usecase()
        if len(usecaseid) > 0:
            postconf_data = self.api_call(self.apis["postprocess_config"], {"usecase_id": usecaseid})
        # postconf_data = pp.api_call("http://172.16.0.204:8000/getpostprocess",{"usecase_id":usecaseid})
        for dt in postconf_data:
            print("========post config=====", dt)
            if dt["usecase_id"] not in postconfigdata.keys():
                postconfigdata[dt["usecase_id"]] = {}
                postconfigdata[dt["usecase_id"]]["image_height"] = dt["image_height"]
                postconfigdata[dt["usecase_id"]]["image_width"] = dt["image_width"]
                postconfigdata[dt["usecase_id"]]["legend"] = dt["legend"]
                postconfigdata[dt["usecase_id"]]["orientation"] = dt["orientation"]
                postconfigdata[dt["usecase_id"]]["postprocess_name"] = dt["postprocess_name"]
                postconfigdata[dt["usecase_id"]]["usecase_name"] = dt["usecase_name"]
                postconfigdata[dt["usecase_id"]]["usecase_description"] = dt["usecase_description"]
                postconfigdata[dt["usecase_id"]]["usecase_template_id"] = dt["usecase_template_id"]
                postconfigdata[dt["usecase_id"]]["incidents"] = {}
                postconfigdata[dt["usecase_id"]]["steps"] = {}
                print("=======step no====")
                print(dt["step_no"])
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]] = {}
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["step_name"] = dt["step_name"]
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["step_type"] = dt["step_type"]
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["computation_id"] = dt["computation_id"]
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["model_id"] = dt["model_id"]

            else:
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]] = {}
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["step_name"] = dt["step_name"]
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["step_type"] = dt["step_type"]
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["computation_id"] = dt["computation_id"]
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["model_id"] = dt["model_id"]
        return postconfigdata

    def incident_postprocess(self, usecase_id, postprocess_data):
        """
        Get incident for each usecase
        Args:
            usecase_id (int or str): usecase data
        returns:
            postprocess_data (list): postprocess data with incident details

        """
        incidentjson = self.api_call(self.apis["incidents"], data={"usecase_id": usecase_id})
        # incidentjson = incidentresponse.json()["data"]
        for inc in incidentjson:
            print("=====inc======")
            print("=====uc======",usecase_id)
            print(inc)
            print(postprocess_data)
            if int(inc["incident_id"]) not in postprocess_data["incidents"]:
                print("=====exist======")
                postprocess_data["incidents"][inc["incident_id"]] = {}
                postprocess_data["incidents"][inc["incident_id"]]["incident_id"] = inc["incident_id"]
                postprocess_data["incidents"][inc["incident_id"]]["incident_name"] = inc["incident_name"]
                postprocess_data["incidents"][inc["incident_id"]]["measurement_unit"] = inc["measurement_unit"]
                postprocess_data["incidents"][inc["incident_id"]]["incident_type_id"] = inc["incident_type_id"]
                postprocess_data["incidents"][inc["incident_id"]]["incident_type_name"] = inc["incident_type_name"]
                
                if "class_id" in postprocess_data["incidents"][inc["incident_id"]] and inc["class_id"] in postprocess_data["incidents"][inc["incident_id"]]["class_id"]:
                    print("======class id exist=====")
                    postprocess_data["incidents"][inc["incident_id"]]["class_id"].append(inc["class_id"])
                else:
                    print("class id not exist")
                    postprocess_data["incidents"][inc["incident_id"]]["class_id"] = [inc["class_id"]]
                
                if "class_name" in postprocess_data["incidents"][inc["incident_id"]] and  inc["class_name"] in postprocess_data["incidents"][inc["incident_id"]]["class_name"]:

                    postprocess_data["incidents"][inc["incident_id"]]["class_name"].append(inc["class_name"])
                else:
                    postprocess_data["incidents"][inc["incident_id"]]["class_name"]=[inc["class_name"]]
            else:
                print("=====exist====")
                print("++++++uc+++++",usecase_id,inc["incident_id"])
                print(postprocess_data["incidents"])
                print(postprocess_data["incidents"][inc["incident_id"]])
                if "class_id" in postprocess_data["incidents"][inc["incident_id"]] and inc["class_id"] not in postprocess_data["incidents"][inc["incident_id"]]["class_id"]:
                    print("====class id exist===")
                    postprocess_data["incidents"][inc["incident_id"]]["class_id"].append(inc["class_id"])
                # else:
                #     print("class id not exist***")
                #     postprocess_data["incidents"][inc["incident_id"]]["class_id"] = [inc["class_id"]]
                
                if "class_name" in postprocess_data["incidents"][inc["incident_id"]] and  inc["class_name"] not  in postprocess_data["incidents"][inc["incident_id"]]["class_name"]:

                    postprocess_data["incidents"][inc["incident_id"]]["class_name"].append(inc["class_name"])
        
        print("&&&&&&uc&&&&&",usecase_id)
        print(postprocess_data["incidents"])

        return postprocess_data

    def step_model(self, usecase_id, postprocess_data):
        """
        Get the assigned model and classes of the usecase
        Args:
            usecase_id (int or str): usecase id
        returns:
            postprocess_data (list): postprocess data with class and model details
        """
        allsteps = postprocess_data["steps"]
        allsteps_keys = allsteps.keys()
        modeldata = self.model_classes(usecase_id)

        for i in modeldata:
            if i["step_no"] in allsteps:
                if "classes" not in allsteps[i["step_no"]]:
                    allsteps[i["step_no"]]["model_url"] = i["model_url"]
                    allsteps[i["step_no"]]["model_type"] = i["model_type"]
                    allsteps[i["step_no"]]["model_framework"] = i["model_framework"]
                    allsteps[i["step_no"]]["classes"] = {}
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]] = {}
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["class_id"] = i["actual_class_id"]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["class_name"] = i["uc_class_name"]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["class_conf"] = i["uc_class_conf"]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["uploaded_class_name"] = i[
                        "uploaded_class_name"
                    ]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["bound_color"] = i["bound_color"]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["bound_thickness"] = i["bound_thickness"]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["text_thickness"] = i["text_thickness"]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["text_color"] = i["text_color"]
                else:
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]] = {}
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["class_id"] = i["actual_class_id"]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["class_name"] = i["uc_class_name"]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["class_conf"] = i["uc_class_conf"]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["uploaded_class_name"] = i[
                        "uploaded_class_name"
                    ]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["bound_color"] = i["bound_color"]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["bound_thickness"] = i["bound_thickness"]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["text_thickness"] = i["text_thickness"]
                    allsteps[i["step_no"]]["classes"][i["actual_class_id"]]["text_color"] = i["text_color"]

        postprocess_data["steps"] = allsteps
        return postprocess_data

    def step_computation(self, usecase_id, postprocess_data):
        """
        Get the assigned computation of the usecase
        Args:
            usecase_id (int or str): usecase id
        returns:
            postprocess_data (list): postprocess data with computation details
        """
        allsteps = postprocess_data["steps"]
        allsteps_keys = allsteps.keys()

        computation = self.computation_data(usecase_id)
        for i in computation:
            if i["step_no"] in allsteps:
                allsteps[i["step_no"]]["lower_limit"] = i["lower_limit"]
                allsteps[i["step_no"]]["upper_limit"] = i["upper_limit"]
                allsteps[i["step_no"]]["tolerance"] = i["tolerance"]
                allsteps[i["step_no"]]["incident_id"] = i["incident_id"]
                allsteps[i["step_no"]]["computation_name"] = i["computation_name"]
        postprocess_data["steps"] = allsteps
        return postprocess_data

    def persist_data(self):
        """
        It combine all the details of use case and send it back to the caching module
        return
            finaldict (list): all usecase postprocess configuration
        """
        finaldict = {}
        postdata_master = self.postprocess_master()
        for usecase_id, postdata in postdata_master.items():
            print("============Get========")
            print(postdata)
            postdata_inc = self.incident_postprocess(usecase_id, postdata)
            postdata_model = self.step_model(usecase_id, postdata_inc)
            postdata_compute = self.step_computation(usecase_id, postdata_model)
            print("=" * 30)
            print(postdata_compute)
            print("#" * 30)
            finaldict[usecase_id] = postdata_compute
        return finaldict
