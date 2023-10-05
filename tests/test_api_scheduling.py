import requests
#scheduling api
api="http://127.0.0.1:8000/getScheduleMaster"

response=requests.get(api,json={})

print("====Response from Scheduling api====")
print(response.json())
print("*************************************")

#Test Schedu
