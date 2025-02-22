import json
import requests
import json


def login(username, password, user):
    data = json.load(open('fixtures/config.json'))
    file_addr = data['users'][user]['file_addr']
    with open(file_addr) as file:
        customer = json.load(file)
    base_url = data['url']['Base']['stage']
    url = base_url + '/login'
    data = {
        "password": "{}".format(password),
        "username": "{}".format(username)
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    token = response.json()['data']['User']['GUID']
    customer['login_info'] = response.json()['data']['User']
    with open(file_addr, 'w') as file:
        json.dump(customer, file, indent=2)
    return token
