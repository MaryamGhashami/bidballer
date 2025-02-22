import json
import requests

def bidders(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']
    url = base_url + '/user/bidders'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response
