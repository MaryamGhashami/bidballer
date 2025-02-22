import json

from services.login import *
from services.terms import *
from services.utils import *
from services.bid import *
from services.lot import *
from services.online import *


def test_accept_terms_add_paddle():
    with open('fixtures/config.json') as file:
        data = json.load(file)
    username = data['users']['second_user']['username']
    password = data['users']['second_user']['password']
    global token
    token = login(username, password, 'second_user')
    body = {"SaleID": 400}
    accept_terms_response = accept_terms(body, token)
    add_paddle_response = add_paddle(body, token)
    paddleNum = add_paddle_response.json()['data']
    data['users']['second_user']['paddleNum'] = paddleNum
    # sale_response = saleInfo({"SaleID": 400}, token)
    # print(sale_response.json())
    # data['sale_info'] = sale_response.json()['data']
    with open('fixtures/config.json', 'w') as file:
        json.dump(data, file, indent=2)

    print("accept_terms_response", accept_terms_response.json())
    print("add_paddle_response", add_paddle_response.json())
    assert accept_terms_response.status_code == 200, "accept terms response returned with {} status code".format(
        accept_terms_response.status_code)
    assert add_paddle_response.status_code == 200, "add paddle response returned with {} status code".format(
        add_paddle_response.status_code)
    assert accept_terms_response.json()['data'] == True, "accept terms response data should be true."
    assert is_numeric(add_paddle_response.json()['data']), "paddle number should be numeric!"


def test_customer_bid():
    conf = json.load(open('fixtures/config.json'))
    with open('fixtures/init_data/second_customer.json') as file:
        data = json.load(file)
    lot_search_body = {
        "SaleID": 400,
        "PageSize": 50,
        "PageIndex": 0,
        "Status": "PRE_SALE"
    }
    response = search(lot_search_body, token)
    for item in data['bidList']:
        item['lotInfo'] = response.json()['data']['lots'][item['lot']]
    with open('fixtures/init_data/second_customer.json', 'w') as file:
        json.dump(data, file, indent=2)
    for val in data['bidList']:
        bid_body = {
            "BidName": val['BidName'],
            "SaleID": data['saleID'],
            "BidValue": val['bidValue'],
            "BidType": val['bidType'],
            "PaddleNumber": conf['users']['second_user']['paddleNum'],
            "LotID": val['lotInfo']['LotID'],
            "LotNumber": "".format(val['lot'])
        }
        print(bid_body)
        response = bid(bid_body, token)
        assert response.status_code == val['expected_status_code'], "biding is failed for lotnumber: {},{}".format(
            val['lot'], response.json())
        if 'budget' in val:
            budgetbody = {
                "Budget": val['budget'],
                "BidName": val['BidName'],
                "SaleID": data['saleID']
            }
            print(budgetbody)
            groupBudgetResponse = groupBudget(budgetbody, token)
            assert groupBudgetResponse.status_code == 200, "group budget setting is failed"


def test_customer_phone_bid_request():
    data = json.load(open('fixtures/init_data/second_customer.json'))
    conf = json.load(open('fixtures/config.json'))
    for val in data['phoneList']:
        phone_bid_body = {
            "SaleID": data['saleID'],
            "LotIDs": [val['LotID']],
            "LotNumbersStr": val['lotNumber']
        }
        print(phone_bid_body)
        response = phoneBid(phone_bid_body, token)
        assert response.status_code == 200, "phone bid is failed for lotnumber: {}".format(val['lotNumber'])


def test_customer_retract():
    data = json.load(open('fixtures/init_data/second_customer.json'))
    for atr in data['retractlist']:
        status = "REQUEST_FOR_RETRACT"
        if (atr['type'] == "all"):
            status = "REQUEST_FOR_RETRACT_ALL_BID"
        res = search(searchBody({"AllBid": True}), token)
        bidId = next((el['Bid']['BidID'] for el in res.json()['data']['lots'] if el['LotID'] == atr['LotID']), None)
        print(bidId)
        retract_body = {
            "SaleID": data['saleID'],
            "BidID": bidId,
            "LotID": atr['LotID'],
            "Status": status
        }
        request_for_retract(retract_body, token)

        print(retract_body)
