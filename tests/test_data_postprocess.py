import requests
import hashlib
import json
response=requests.get("http://localhost:8000/getpostprocess",json={"usecase_id":[1]})
# print(response.json()["data"])
postconf_data=response.json()["data"]
postconfigdata={}
for dt in postconf_data:
    print("=====",dt)
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
        incidentresponse=requests.get("http://localhost:8000/getincidents",json={"usecase_id":1})
        incidentjson= incidentresponse.json()["data"]
        for inc in incidentjson:
            postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]={}
            postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]["incident_name"]=inc["incident_name"]
            postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]["measurement_unit"]=inc["measurement_unit"]
            postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]["incident_type_id"]=inc["incident_type_id"]
            postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]["incident_type_name"]=inc["incident_type_name"]
            postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]["class_id"]=inc["class_id"]
            postconfigdata[dt["usecase_id"]]["incidents"][inc["incident_id"]]["class_name"]=inc["class_name"]
            
            






        if dt["model_id"] is not None:
            classresponse=requests.get("http://localhost:8000/getclasses",json={"usecase_id":1})
            modeldata=classresponse.json()["data"]

            for md in modeldata:
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["model_url"]=md["model_url"]

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
            computationresponse=requests.get("http://localhost:8000/getcomputation",json={"usecase_id":2})
            computationdata=computationresponse.json()["data"]
            compute=computationdata[0]
            #print("*******",computationdata)
            # for compute in computationdata:
                #postconfigdata[dt["usecase_id"]]["steps"]["computation"]={}
                #postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["computation_id"]=compute["computation_id"]
            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["lower_limit"]=compute["lower_limit"]
            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["upper_limit"]=compute["upper_limit"]
            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["tolerance"]=compute["tolerance"]
    else:
            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]={}
            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["step_name"]=dt["step_name"]
            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["step_type"]=dt["step_type"]
            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["computation_id"]=dt["computation_id"]
            postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["model_id"]=dt["model_id"]
            if dt["model_id"] is not None:
                response=requests.get("http://localhost:8000/getclasses",json={"usecase_id":1})
                modeldata=response.json()["data"]

                for md in modeldata:
                    postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["model_url"]=md["model_url"]

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
                computationresponse=requests.get("http://localhost:8000/getcomputation",json={"usecase_id":2})
                computationdata=computationresponse.json()["data"]
                
                print("*******",computationdata)
                compute=computationdata[0]
                #for compute in computationdata:
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["lower_limit"]=compute["lower_limit"]
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["upper_limit"]=compute["upper_limit"]
                postconfigdata[dt["usecase_id"]]["steps"][dt["step_no"]]["tolerance"]=compute["tolerance"]


print(postconfigdata)
print(hashlib.sha256(str(postconfigdata).encode()).hexdigest())
print(json.dumps(postconfigdata,indent=4))   