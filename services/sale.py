import json
import requests


def saleInfo(query, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/sale/connectionInfo/' + query
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.get(url, headers=headers)
    return response


def bidders(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/sale/bidders'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response
