import requests
#preprocess api
api="http://127.0.0.1:8000/getPreprocessConfig"


response=requests.get(api,json={})

print("====Response from Scheduling api====")
print(response.json())
print("*************************************")
