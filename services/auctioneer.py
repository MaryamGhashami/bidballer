import json
import requests




def auctioneer(body, token):
    f = open('fixtures/config.json')
    data = json.load(f)
    base_url = data['url']['CSGateWay']['stage']

    url = base_url + '/auctioneer/event'
    headers = {"Content-Type": "application/json",
               "Authorization": "{}".format(token)}
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response


