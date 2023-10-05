url="http://localhost:8000/getboundary"
import requests
import hashlib
import json
response=requests.get(url,json={"usecase_id":[1]})
print(response.json())
boundarydata=response.json()["data"]
boundaryconfig={}
for bd in boundarydata:
    if bd["camera_id"] not in  boundaryconfig:
        boundaryconfig[bd["camera_id"]]={}
        # if bd["usecase_id"] not in 
        boundaryconfig[bd["camera_id"]][bd["usecase_id"]]={}
        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]={}
        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]={}
        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]["x"] =[bd["x_coordinate"]]
        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]["y"] =[bd["y_coordinate"]]
    else:
        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]["x"].append(bd["x_coordinate"])
        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"]["y"].append(bd["y_coordinate"])



print(boundaryconfig)
