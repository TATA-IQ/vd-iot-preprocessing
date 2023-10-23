"""
Boundary Configuration
"""
import requests


class PersistBoundaryConfig:
    def __init__(self, apis):
        """
        Saving Boundary Config To Cache
        Args:
            apis (list): list of apis


        """
        self.apis = apis
        self.postprocessdata = None

    def api_call(self, url, query: dict = None) -> list:
        """
        Call the api for boundary config
        Args:
            url (str): url
            query (dict or json): request query
        returns:
            boundary_data (list): detail  data of requested query
        """
        cameraconfdata = []
        boundary_data = []
        if query is None:
            print("None")
            resposnse_boundary = requests.get(url, json={}, timeout=50)
        else:
            resposnse_boundary = requests.get(url, json=query, timeout=50)
        # print(resposnse)
        # print(resposnse.json())
        print(url, query)
        if resposnse_boundary.status_code == 200:
            boundary_data = resposnse_boundary.json()["data"]
        return boundary_data

    def get_usecase(self, usecase_url):
        """
        Call the api for Usecase list
        Args:
            usecase_url (str): request url
        returns:
           usecaseres (list): detail  data of requested query
        """
        usecaseres = self.api_call(usecase_url)
        if len(usecaseres) > 0:
            return usecaseres["usecase_id"]
        else:
            return []

    def persist_data(self):
        """
        Format the boundary data as json configuration
        return:
            boundaryconfig (dict): boundary configuration dict, usecase will be on key level.

        """
        usecaselist = self.get_usecase(self.apis["usecase_urls"])
        boundaryconfig = {}
        if len(usecaselist) > 0:
            boundarydata = self.api_call(self.apis["boundary_config"], {"usecase_id": usecaselist})
            # boundarydata

            for bd in boundarydata:
                print(bd)
                if bd["camera_id"] not in boundaryconfig:
                    boundaryconfig[bd["camera_id"]] = {}
                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]] = {}
                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]] = {}
                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"] = {}
                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"][
                        "x"
                    ] = [bd["x_coordinate"]]
                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"][
                        "y"
                    ] = [bd["y_coordinate"]]
                else:
                    print("===else===")
                    if bd["boundary_id"] not in boundaryconfig[bd["camera_id"]][bd["usecase_id"]]:
                        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]] = {}
                        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]][
                            "boundary_coordinates"
                        ] = {}
                        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"][
                            "x"
                        ] = [bd["x_coordinate"]]
                        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"][
                            "y"
                        ] = [bd["y_coordinate"]]
                    else:
                        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"][
                            "x"
                        ].append(bd["x_coordinate"])
                        boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"][
                            "y"
                        ].append(bd["y_coordinate"])

                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"][
                        "x"
                    ].append(bd["x_coordinate"])
                    boundaryconfig[bd["camera_id"]][bd["usecase_id"]][bd["boundary_id"]]["boundary_coordinates"][
                        "y"
                    ].append(bd["y_coordinate"])
        return boundaryconfig
