import requests

class PersistBoundaryConfig():
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
        boundaryconfig={}
        if len(usecaselist)>0:

            boundarydata=self.apiCall(self.apis["boundary_config"],{"usecase_id":usecaselist})
            #boundarydata
            
            for bd in boundarydata:
                print(bd)
                if bd["camera_id"] not in  boundaryconfig:
                    boundaryconfig[bd["camera_id"]]={}
                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]]={}
                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]={}
                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]={}
                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]["x"] =[bd["x_coordinate"]]
                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]["y"] =[bd["y_coordinate"]]
                else:
                    print("===else===")
                    if bd["boundary_id"] not  in boundaryconfig[bd["camera_id"]][bd["usecase_id"]]:
                        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]={}
                        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]={}
                        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]["x"] =[bd["x_coordinate"]]
                        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]["y"] =[bd["y_coordinate"]]
                    else:
                        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]["x"].append(bd["x_coordinate"])
                        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]["y"].append(bd["y_coordinate"])
        
                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]["x"].append(bd["x_coordinate"])
                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]["y"].append(bd["y_coordinate"])
        return boundaryconfig