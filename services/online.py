import json
import requests


def clerkList(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/online/clerkList'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response


def nextprev(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/online/lot/info/nextprev'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response.json()


def lastSoldLot(query, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/online/lastSoldLot/' + query
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.get(url, headers=headers)
    return response


def statistics(query, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/online/statistics/' + query
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.get(url, headers=headers)
    return response


def lots(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/online/lots'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    print(url)
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response


def saleInfo(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/online/saleinfo'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    print(url)
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response


def relatedBids(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/online/relatedBids'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    print(url)
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response


