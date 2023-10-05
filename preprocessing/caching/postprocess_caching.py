import requests

class PersistPostProcessConfig():
    def __init__(self, apis):
        self.apis = apis
        self.postprocessdata = None

    def apiCall(self, url,data: dict = None) -> list:
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
            resposnse = requests.get(url, json={}, timeout=50)
        else:
            resposnse = requests.get(url, json=data, timeout=50)
        # print(resposnse)
        # print(resposnse.json())
        print(url,data)
        if resposnse.status_code == 200:
            postprocessdata = resposnse.json()["data"]
        return postprocessdata
    def get_usecase(self,usecase_url):
        usecaseres=self.apiCall(usecase_url)
        if len(usecaseres)>0:
            return usecaseres["usecase_id"]
        else:
            return []
    def persistData(self):
        usecaselist=self.get_usecase(self.apis["usecase_urls"])
        usecaselist=[2]
        if len(usecaselist)>0:

            postconf_data=self.apiCall(self.apis["postprocess_config"],{"usecase_id":usecaselist})
            postconfigdata={}
            print("======")
            for dt in postconf_data:
                print("========post config=====",dt)
                if dt["usecase_id"] not in postconfigdata.keys():
                    postconfigdata[dt["usecase_id"]]={}
                    postconfigdata[dt["usecase_id"]]["image_height"]=dt["image_height"]
                    postconfigdata[dt["usecase_id"]]["image_width"]=dt["image_width"]
                    postconfigdata[dt["usecase_id"]]["legend"]=dt["legend"]
                    postconfigdata[dt["usecase_id"]]["postprocess_name"]=dt["postprocess_name"]
                    postconfigdata[dt["usecase_id"]]["usecase_name"]=dt["usecase_name"]
                    postconfigdata[dt["usecase_id"]]["usecase_description"]=dt["usecase_description"]
                    postconfigdata[dt["usecase_id"]]["usecase_template_id"]=dt["usecase_template_id"]
                    postconfigdata[dt["usecase_id"]]["incidents"]={}
                    postconfigdata[dt["usecase_id"]]["steps"]={}
                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]={}
                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["step_name"]=dt["step_name"]
                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["step_type"]=dt["step_type"]
                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["computation_id"]=dt["computation_id"]
                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["model_id"]=dt["model_id"]
                    incidentresponse=requests.get(self.apis["incidents"],json={"usecase_id":dt["usecase_id"]})
                    incidentjson= incidentresponse.json()["data"]
                    print("========incident json========")
                    print(incidentjson)
                    for inc in incidentjson:
                        
                        postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]={}
                        postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]["incident_id"]=inc["incident_id"]
                        postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]["incident_name"]=inc["incident_name"]
                        postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]["measurement_unit"]=inc["measurement_unit"]
                        postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]["incident_type_id"]=inc["incident_type_id"]
                        postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]["incident_type_name"]=inc["incident_type_name"]
                        postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]["class_id"]=inc["class_id"]
                        postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]["class_name"]=inc["class_name"]
                        
                        






                    if dt["model_id"] is not None:
                        classresponse=requests.get(self.apis["classes"],json={"usecase_id":dt["usecase_id"]})
                        modeldata=classresponse.json()["data"]
                        print("********ModelData=======",dt["model_id"])
                        print(modeldata)


                        for md in modeldata:
                            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["model_url"]=md["model_url"]
                            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["model_type"]=md["model_type"]
                            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["model_framework"]=md["model_framework"]

                            if "classes" not in list(postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]].keys()):
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"]={}
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]={}
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["class_id"]=md["actual_class_id"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["class_name"]=md["uc_class_name"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["class_conf"]=md["uc_class_conf"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["uploaded_class_name"]=md["uploaded_class_name"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["bound_color"]=md["bound_color"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["bound_thickness"]=md["bound_thickness"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["text_thickness"]=md["text_thickness"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["text_color"]=md["text_color"]

                            else:
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]={}
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["class_id"]=md["actual_class_id"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["class_name"]=md["uc_class_name"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["class_conf"]=md["uc_class_conf"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["uploaded_class_name"]=md["uploaded_class_name"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["bound_color"]=md["bound_color"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["bound_thickness"]=md["bound_thickness"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["text_thickness"]=md["text_thickness"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["text_color"]=md["text_color"]


                    if dt["computation_id"] is not None:
                        print("====inside compute===")
                        computationresponse=requests.get(self.apis["computation"],json={"usecase_id":dt["usecase_id"]})
                        computationdata=computationresponse.json()["data"]
                        compute=computationdata[0]
                        #print("*******",computationdata)
                        # for compute in computationdata:
                            #postconfigdata[dt["usecase_id"]]["steps"]["computation"]={}
                            #postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["computation_id"]=compute["computation_id"]
                        postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["lower_limit"]=compute["lower_limit"]
                        postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["upper_limit"]=compute["upper_limit"]
                        postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["tolerance"]=compute["tolerance"]
                        postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["incident_id"]=compute["incident_id"]
                        postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["computation_name"]=compute["computation_name"]
                else:
                        postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]={}
                        postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["step_name"]=dt["step_name"]
                        postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["step_type"]=dt["step_type"]
                        postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["computation_id"]=dt["computation_id"]
                        postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["model_id"]=dt["model_id"]
                        if dt["model_id"] is not None:
                            response=requests.get(self.apis["classes"],json={"usecase_id":dt["usecase_id"]})
                            modeldata=response.json()["data"]
                            print("********",modeldata)

                            for md in modeldata:
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["model_url"]=md["model_url"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["model_type"]=md["model_type"]
                                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["model_framework"]=md["model_framework"]


                                if "classes" not in list(postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]].keys()):
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"]={}
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]={}
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["class_id"]=md["actual_class_id"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["class_name"]=md["uc_class_name"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["class_conf"]=md["uc_class_conf"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["uploaded_class_name"]=md["uploaded_class_name"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["bound_color"]=md["bound_color"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["bound_thickness"]=md["bound_thickness"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["text_thickness"]=md["text_thickness"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["text_color"]=md["text_color"]
                                else:
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]={}
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["class_id"]=md["actual_class_id"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["class_name"]=md["uc_class_name"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["class_conf"]=md["uc_class_conf"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["uploaded_class_name"]=md["uploaded_class_name"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["bound_color"]=md["bound_color"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["bound_thickness"]=md["bound_thickness"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["text_thickness"]=md["text_thickness"]
                                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["classes"][md["actual_class_id"]]["text_color"]=md["text_color"]

                        if dt["computation_id"] is not None:
                            computationresponse=requests.get(self.apis["computation"],json={"usecase_id":dt["usecase_id"]})
                            computationdata=computationresponse.json()["data"]
                            
                            print("*******",computationdata)
                            compute=computationdata[0]
                            #for compute in computationdata:
                            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["incident_id"]=compute["incident_id"]
                            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["computation_name"]=compute["computation_name"]
                            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["lower_limit"]=compute["lower_limit"]
                            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["upper_limit"]=compute["upper_limit"]
                            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["tolerance"]=compute["tolerance"]
        return postconfigdata





