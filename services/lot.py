import json
import requests

def phoneBid(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/lot/phoneBid/request'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    # if response.status_code == 200:
    #     assert response.status_code == 200, f"biding failed with status code {response.status_code}"
    # else:
    #     print('biding failed')
    return response


def phoneBidList(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/lot/phoneBid/customer/list'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    # if response.status_code == 200:
    #     assert response.status_code == 200, f"biding failed with status code {response.status_code}"
    # else:
    #     print('biding failed')
    return response


def search(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/lot/search'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response


def lastStatus(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/lot/pre/lastStatus'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response


def phoneBidChangeStatus(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/lot/phoneBid/changeStatus'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.put(url, data=json.dumps(body), headers=headers)
    return response


