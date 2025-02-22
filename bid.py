import json
import requests

def bid(body,token):
    # driver = webdriver.Chrome()
    url = 'http://192.168.2.78:8087/bid'
    data = body
    headers = {"Content-Type":"application/json",
               "Authorization":"{}".format(token)}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(response.json())
    if response.status_code == 200:
        # print(response.json()['data']['User']['GUID'])
        # token = response.json()['data']['User']['GUID']
        assert response.status_code == 200, f"Login failed with status code {response.status_code}"
    else:
        print('failed')

    return response

def accept_terms(body,token):
    url= 'http://192.168.2.78:8087/terms/accept'
    data = body
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(response.json())

    if response.status_code == 200:
        # print(response.json())
        # token = response.json()['data']['User']['GUID']
        assert response.status_code == 200, f"Login failed with status code {response.status_code}"
    else:
        print('accepting terms failed')

