import json
import requests

f = open('fixtures/config.json')


def accept_terms(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/terms/accept'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response


def check_register(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/terms/isAccepted'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response


def add_paddle(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/terms/addPaddle'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response


def update_paddle(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/terms/updatePaddle'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.put(url, data=json.dumps(body), headers=headers)
    return response


def delete_paddle(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/terms/deletePaddle'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response
