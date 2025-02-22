import json
import threading
import time
import pytest
from services.login import login
from services.bid import bid, retract
from services.online import clerkList, relatedBids
from services.auctioneer import auctioneer
from fixtures.socket_clients.fixtures import socket_clerk_client, socket_firstCustomer_client, \
    socket_secondCustomer_client
from services.utils import *

lot_number = 9
user1_token = json.load(open('fixtures/init_data/first_customer.json'))['login_info']['GUID']
user2_token = json.load(open('fixtures/init_data/second_customer.json'))['login_info']['GUID']
clerk_token = json.load(open('fixtures/first_clerk.json'))['login_info']['GUID']


def test_group_status_in_related_bids(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    clerk_data = json.load(open('fixtures/first_clerk.json'))
    lotId = next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number - 1)))
    Bidname = next((bid['BidName'] for bid in data['bidList'] if bid.get("lot") == (lot_number - 1)))
    BidVal = next((bid['bidValue'] for bid in data['bidList'] if bid.get("lot") == (lot_number - 1)))
    body = {
        "SaleID": 1369,
        "UserID": data['login_info']['UserID'],
        "LotID": lotId,
        "BidName": Bidname
    }
    print(body)
    clerkList_response = clerkList({"SaleID": 1369,
                                    "LotID": lotId}, clerk_data['login_info']['GUID'])
    relatedBids_response = relatedBids(body, data['login_info']['GUID'])
    print("-------------------------", clerkList_response.json())
    Server_adjValue = next(
        bid['AdjustValue'] for bid in clerkList_response.json()['data']['Bids'] if bid.get("GroupBid") == Bidname)
    assert relatedBids_response.status_code == 200, "related bids response status code is not 200"
    assert clerkList_response.status_code == 200, "clerk list response status code is not 200"
    assert Server_adjValue == adjValue(relatedBids_response.json()['data']['RemainingBudget'],
                                       BidVal), "adj value is wrong!"
    assert relatedBids_response.json()['data']['List'][0]['Status'] == None, "status of or bid is wrong!"
    assert relatedBids_response.json()['data']['List'][1]['Status'] == None, "status of or bid is wrong!"
    assert relatedBids_response.json()['data']['List'][2]['Status'] == None, "status of or bid is wrong!"
    assert relatedBids_response.json()['data']['List'][3]['Status'] == None, "status of or bid is wrong!"


def test_open_lot_by_clerk(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    received_events_2_by_clerk = []
    event_2_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()
    received_events_3_by_clerk = []
    event_3_received_by_clerk = threading.Event()

    @socket_clerk_client.on('2')
    def event_1(data):
        # print("received event '2':", data)
        received_events_2_by_clerk.append(json.loads(data))
        event_2_received_by_clerk.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

    @socket_clerk_client.on('3')
    def event_1(data):
        # print("received event '3':", data)
        received_events_3_by_clerk.append(json.loads(data))
        event_3_received_by_clerk.set()

        # start

    time.sleep(0.1)
    body = {
        "SaleID": 1369,
        "LotID": next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number - 1))),
        "MinBid": "8500",
        "Event": "SET_MIN_BID_AND_OPEN_LOT"
    }
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_2_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_3_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_2_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_2_by_clerk[0]['Lot']['Status'] == "IN_SALE", "lot status is wrong"
    assert len(received_events_2_by_clerk) > 0, "No events received by clerk"
    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #9 opened at $8,500", "Log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
    assert event_3_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_3_by_clerk[0]['OpeningBasePrice'] == 8500, "opening price is wrong"
    assert len(received_events_3_by_clerk) > 0, "No events received by clerk"


def test_close_lot_by_clerk_and_determine_the_winner(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    received_events_4_by_clerk = []
    event_4_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()

    @socket_clerk_client.on('4')
    def event_1(data):
        # print("received event '4':", data)
        received_events_4_by_clerk.append(json.loads(data))
        event_4_received_by_clerk.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

        # start

    time.sleep(0.2)
    body = {"SaleID": 1369, "Event": "FINISHED_LOT_TIME",
            "LotID": next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number - 1)))}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_4_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_4_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_4_by_clerk[0]['Status'] == "SOLD", "sale status is wrong"
    assert received_events_4_by_clerk[0]['MaxBid']['Role'] == "CUSTOMER", "sale status is wrong"
    assert len(received_events_4_by_clerk) > 0, "No events received by clerk"

    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #9 closed", "log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"


def test_group_status_in_related_bids_after_winnig_first_one(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    lotId = next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number - 1)))
    Bidname = next((bid['BidName'] for bid in data['bidList'] if bid.get("lot") == (lot_number - 1)))
    body = {
        "SaleID": 1369,
        "UserID": data['login_info']['UserID'],
        "LotID": lotId,
        "BidName": Bidname
    }
    print(body)
    response = relatedBids(body, data['login_info']['GUID'])

    assert response.status_code == 200, "response status code is not 200"
    assert response.json()['data']['RemainingBudget'] == 1000, "remaining budget is wrong"
    assert response.json()['data']['List'][0]['Status'] == "WON", "status of or bid is wrong!"
    assert response.json()['data']['List'][1]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][2]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][3]['Status'] == None, "status of or bid is wrong!"


def test_open_second_lot_by_clerk(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    received_events_2_by_clerk = []
    event_2_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()
    received_events_3_by_clerk = []
    event_3_received_by_clerk = threading.Event()

    @socket_clerk_client.on('2')
    def event_1(data):
        # print("received event '2':", data)
        received_events_2_by_clerk.append(json.loads(data))
        event_2_received_by_clerk.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

    @socket_clerk_client.on('3')
    def event_1(data):
        # print("received event '3':", data)
        received_events_3_by_clerk.append(json.loads(data))
        event_3_received_by_clerk.set()

        # start

    time.sleep(0.1)
    body = {
        "SaleID": 1369,
        "LotID": next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number))),
        "MinBid": "2000",
        "Event": "SET_MIN_BID_AND_OPEN_LOT"
    }
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_2_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_3_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_2_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_2_by_clerk[0]['Lot']['Status'] == "IN_SALE", "lot status is wrong"
    assert len(received_events_2_by_clerk) > 0, "No events received by clerk"
    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #10 opened at $2,000", "Log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
    assert event_3_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_3_by_clerk[0]['OpeningBasePrice'] == 2000, "opening price is wrong"
    assert len(received_events_3_by_clerk) > 0, "No events received by clerk"


def test_close_second_lot_by_clerk_and_determine_the_winner(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    received_events_4_by_clerk = []
    event_4_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()

    @socket_clerk_client.on('4')
    def event_1(data):
        # print("received event '4':", data)
        received_events_4_by_clerk.append(json.loads(data))
        event_4_received_by_clerk.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

        # start

    time.sleep(0.2)
    body = {"SaleID": 1369, "Event": "FINISHED_LOT_TIME",
            "LotID": next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number)))}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_4_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_4_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_4_by_clerk[0]['Status'] == "NOT_SOLD", "sale status is wrong"
    assert received_events_4_by_clerk[0]['MaxBid']['Role'] == "CLERK", "sale status is wrong"
    assert len(received_events_4_by_clerk) > 0, "No events received by clerk"

    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #10 closed", "log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"


def test_group_status_in_related_bids_after_opening_second_lot(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    lotId = next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number)))
    Bidname = next((bid['BidName'] for bid in data['bidList'] if bid.get("lot") == (lot_number)))
    BidVal = next((bid['bidValue'] for bid in data['bidList'] if bid.get("lot") == (lot_number)))
    body = {
        "SaleID": 1369,
        "UserID": data['login_info']['UserID'],
        "LotID": lotId,
        "BidName": Bidname
    }
    print(body)
    # clerkList_response = clerkList({"SaleID": 1369,
    #                                 "LotID": lotId}, data['login_info']['GUID'])
    relatedBids_response = relatedBids(body, data['login_info']['GUID'])
    # Server_adjValue = next(
    #     bid['AdjustValue'] for bid in clerkList_response.json()['data']['Bids'] if bid.get("GroupBid") == Bidname)
    assert relatedBids_response.status_code == 200, "related bids response status code is not 200"
    # assert clerkList_response.status_code == 200, "clerk list response status code is not 200"
    # assert Server_adjValue == adjValue(relatedBids_response.json()['data']['RemainingBudget'],
    #                                    BidVal), "adj value is wrong!"
    assert relatedBids_response.json()['data']['List'][0]['Status'] == "WON", "status of or bid is wrong!"
    assert relatedBids_response.json()['data']['List'][1]['Status'] == None, "status of or bid is wrong!"
    assert relatedBids_response.json()['data']['List'][2]['Status'] == None, "status of or bid is wrong!"
    assert relatedBids_response.json()['data']['List'][3]['Status'] == None, "status of or bid is wrong!"


def test_reopen_second_lot_with_editing_opening_price(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    received_events_2_by_clerk = []
    event_2_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()
    received_events_3_by_clerk = []
    event_3_received_by_clerk = threading.Event()

    @socket_clerk_client.on('2')
    def event_1(data):
        # print("received event '2':", data)
        received_events_2_by_clerk.append(json.loads(data))
        event_2_received_by_clerk.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

    @socket_clerk_client.on('3')
    def event_1(data):
        # print("received event '3':", data)
        received_events_3_by_clerk.append(json.loads(data))
        event_3_received_by_clerk.set()

        # start

    time.sleep(0.1)
    body = {
        "SaleID": 1369,
        "LotID": next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number))),
        "MinBid": "450",
        "Event": "SET_MIN_BID_AND_OPEN_LOT"
    }
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_2_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_3_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_2_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_2_by_clerk[0]['Lot']['Status'] == "IN_SALE", "lot status is wrong"
    assert len(received_events_2_by_clerk) > 0, "No events received by clerk"
    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #10 opened at $450", "Log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
    assert event_3_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_3_by_clerk[0]['OpeningBasePrice'] == 450, "opening price is wrong"
    assert len(received_events_3_by_clerk) > 0, "No events received by clerk"


def test_close_second_lot_by_clerk_and_determine_the_winner_after_reopening(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    received_events_4_by_clerk = []
    event_4_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()

    @socket_clerk_client.on('4')
    def event_1(data):
        # print("received event '4':", data)
        received_events_4_by_clerk.append(json.loads(data))
        event_4_received_by_clerk.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

        # start

    time.sleep(0.2)
    body = {"SaleID": 1369, "Event": "FINISHED_LOT_TIME",
            "LotID": next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number)))}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_4_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_4_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_4_by_clerk[0]['Status'] == "SOLD", "sale status is wrong"
    assert received_events_4_by_clerk[0]['MaxBid']['Role'] == "CUSTOMER", "sale status is wrong"
    assert len(received_events_4_by_clerk) > 0, "No events received by clerk"

    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #10 closed", "log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"


def test_group_status_in_related_bids_after_closing_second_lot(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    lotId = next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number)))
    Bidname = next((bid['BidName'] for bid in data['bidList'] if bid.get("lot") == (lot_number)))
    BidVal = next((bid['bidValue'] for bid in data['bidList'] if bid.get("lot") == (lot_number)))
    body = {
        "SaleID": 1369,
        "UserID": data['login_info']['UserID'],
        "LotID": lotId,
        "BidName": Bidname
    }
    print(body)
    # clerkList_response = clerkList({"SaleID": 1369,
    #                                 "LotID": lotId}, data['login_info']['GUID'])
    relatedBids_response = relatedBids(body, data['login_info']['GUID'])
    # Server_adjValue = next(
    #     bid['AdjustValue'] for bid in clerkList_response.json()['data']['Bids'] if bid.get("GroupBid") == Bidname)
    assert relatedBids_response.status_code == 200, "related bids response status code is not 200"
    # assert clerkList_response.status_code == 200, "clerk list response status code is not 200"
    # assert Server_adjValue == adjValue(relatedBids_response.json()['data']['RemainingBudget'],
    #                                    BidVal), "adj value is wrong!"
    assert relatedBids_response.json()['data']['List'][0]['Status'] == "WON", "status of or bid is wrong!"
    assert relatedBids_response.json()['data']['List'][1]['Status'] == "WON", "status of or bid is wrong!"
    assert relatedBids_response.json()['data']['List'][2]['Status'] == None, "status of or bid is wrong!"
    assert relatedBids_response.json()['data']['List'][3]['Status'] == None, "status of or bid is wrong!"


def test_open_third_lot_by_clerk(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    received_events_2_by_clerk = []
    event_2_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()
    received_events_3_by_clerk = []
    event_3_received_by_clerk = threading.Event()

    @socket_clerk_client.on('2')
    def event_1(data):
        # print("received event '2':", data)
        received_events_2_by_clerk.append(json.loads(data))
        event_2_received_by_clerk.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

    @socket_clerk_client.on('3')
    def event_1(data):
        # print("received event '3':", data)
        received_events_3_by_clerk.append(json.loads(data))
        event_3_received_by_clerk.set()

        # start

    time.sleep(0.1)
    body = {
        "SaleID": 1369,
        "LotID": next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 1))),
        "MinBid": "100",
        "Event": "SET_MIN_BID_AND_OPEN_LOT"
    }
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_2_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_3_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_2_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_2_by_clerk[0]['Lot']['Status'] == "IN_SALE", "lot status is wrong"
    assert len(received_events_2_by_clerk) > 0, "No events received by clerk"
    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #11 opened at $100", "Log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
    assert event_3_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_3_by_clerk[0]['OpeningBasePrice'] == 100, "opening price is wrong"
    assert len(received_events_3_by_clerk) > 0, "No events received by clerk"


def test_first_biding_with_first_customers_and_receiving_events_with_customer_and_clerk(socket_clerk_client,
                                                                                        socket_firstCustomer_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    lotId = next((BID['lotInfo']['LotID'] for BID in data['bidList'] if BID.get("lot") == (lot_number + 1)))
    Bidname = next((BID['BidName'] for BID in data['bidList'] if BID.get("lot") == (lot_number + 1)))
    BidVal = next((BID['bidValue'] for BID in data['bidList'] if BID.get("lot") == (lot_number + 1)))
    conf = json.load(open('fixtures/config.json'))
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()
    received_events_by_firstCustomer = []
    event_received_by_firstCustomer = threading.Event()

    @socket_clerk_client.on('29')
    def event_1(data):
        # print("received event '29':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

    @socket_firstCustomer_client.on('27')
    def event_1(data):
        # print("received event '27':", data)
        received_events_by_firstCustomer.append(json.loads(data))
        event_received_by_firstCustomer.set()

        # start

    time.sleep(0.1)
    body_bid_user1 = {"SaleID": 1369, "LotID": lotId, "LotNumber": lot_number + 1, "BidValue": 450,
                      "PaddleNumber": conf['users']['first_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}
    res_1 = bid(body_bid_user1, user1_token)
    # Wait for the event to be received or timeout after a certain duration
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_received_by_firstCustomer.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received"
    assert received_events_by_clerk[0]['id'], ""
    assert len(received_events_by_clerk) > 0, "No events received"
    assert event_received_by_firstCustomer.is_set(), "Event not received"
    assert received_events_by_firstCustomer[0]['id'], ""
    assert len(received_events_by_firstCustomer) > 0, "No events received"


def test_group_status_in_related_bids_after_first_biding_on_third_lot(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    lotId = next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 1)))
    Bidname = next((bid['BidName'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 1)))
    body = {
        "SaleID": 1369,
        "UserID": data['login_info']['UserID'],
        "LotID": lotId,
        "BidName": Bidname
    }
    print(body)
    response = relatedBids(body, data['login_info']['GUID'])

    assert response.status_code == 200, "response status code is not 200"
    # assert response.json()['data']['RemainingBudget'] == 1000, "remaining budget is wrong"
    assert response.json()['data']['List'][0]['Status'] == "WON", "status of or bid is wrong!"
    assert response.json()['data']['List'][1]['Status'] == "WON", "status of or bid is wrong!"
    assert response.json()['data']['List'][2]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][3]['Status'] == None, "status of or bid is wrong!"


def test_second_biding_with_first_customers_and_receiving_events_with_customer_and_clerk(socket_clerk_client,
                                                                                         socket_firstCustomer_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    lotId = next((BID['lotInfo']['LotID'] for BID in data['bidList'] if BID.get("lot") == (lot_number + 1)))
    Bidname = next((BID['BidName'] for BID in data['bidList'] if BID.get("lot") == (lot_number + 1)))
    BidVal = next((BID['bidValue'] for BID in data['bidList'] if BID.get("lot") == (lot_number + 1)))
    conf = json.load(open('fixtures/config.json'))
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()
    received_events_by_firstCustomer = []
    event_received_by_firstCustomer = threading.Event()

    @socket_clerk_client.on('29')
    def event_1(data):
        # print("received event '29':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

    @socket_firstCustomer_client.on('27')
    def event_1(data):
        # print("received event '27':", data)
        received_events_by_firstCustomer.append(json.loads(data))
        event_received_by_firstCustomer.set()

        # start

    time.sleep(0.1)
    body_bid_user1 = {"SaleID": 1369, "LotID": lotId, "LotNumber": lot_number + 1, "BidValue": 500,
                      "PaddleNumber": conf['users']['first_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}
    res_1 = bid(body_bid_user1, user1_token)
    # Wait for the event to be received or timeout after a certain duration
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_received_by_firstCustomer.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received"
    assert received_events_by_clerk[0]['id'], ""
    assert len(received_events_by_clerk) > 0, "No events received"
    assert event_received_by_firstCustomer.is_set(), "Event not received"
    assert received_events_by_firstCustomer[0]['id'], ""
    assert len(received_events_by_firstCustomer) > 0, "No events received"


def test_group_status_in_related_bids_after_second_biding_on_third_lot(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    lotId = next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 1)))
    Bidname = next((bid['BidName'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 1)))
    body = {
        "SaleID": 1369,
        "UserID": data['login_info']['UserID'],
        "LotID": lotId,
        "BidName": Bidname
    }
    print(body)
    response = relatedBids(body, data['login_info']['GUID'])

    assert response.status_code == 200, "response status code is not 200"
    # assert response.json()['data']['RemainingBudget'] == 1000, "remaining budget is wrong"
    assert response.json()['data']['List'][0]['Status'] == "WON", "status of or bid is wrong!"
    assert response.json()['data']['List'][1]['Status'] == "WON", "status of or bid is wrong!"
    assert response.json()['data']['List'][2]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][3]['Status'] == None, "status of or bid is wrong!"


def test_third_biding_with_first_customers_and_receiving_events_with_customer_and_clerk(socket_clerk_client,
                                                                                        socket_firstCustomer_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    lotId = next((BID['lotInfo']['LotID'] for BID in data['bidList'] if BID.get("lot") == (lot_number + 1)))
    Bidname = next((BID['BidName'] for BID in data['bidList'] if BID.get("lot") == (lot_number + 1)))
    BidVal = next((BID['bidValue'] for BID in data['bidList'] if BID.get("lot") == (lot_number + 1)))
    conf = json.load(open('fixtures/config.json'))
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()
    received_events_by_firstCustomer = []
    event_received_by_firstCustomer = threading.Event()

    @socket_clerk_client.on('29')
    def event_1(data):
        # print("received event '29':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

    @socket_firstCustomer_client.on('27')
    def event_1(data):
        # print("received event '27':", data)
        received_events_by_firstCustomer.append(json.loads(data))
        event_received_by_firstCustomer.set()

        # start

    time.sleep(0.1)
    body_bid_user1 = {"SaleID": 1369, "LotID": lotId, "LotNumber": lot_number + 1, "BidValue": 700,
                      "PaddleNumber": conf['users']['first_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}
    res_1 = bid(body_bid_user1, user1_token)
    # Wait for the event to be received or timeout after a certain duration
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_received_by_firstCustomer.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received"
    assert received_events_by_clerk[0]['id'], ""
    assert len(received_events_by_clerk) > 0, "No events received"
    assert event_received_by_firstCustomer.is_set(), "Event not received"
    assert received_events_by_firstCustomer[0]['id'], ""
    assert len(received_events_by_firstCustomer) > 0, "No events received"


def test_close_third_lot_by_clerk_and_determine_the_winner(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    received_events_4_by_clerk = []
    event_4_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()

    @socket_clerk_client.on('4')
    def event_1(data):
        # print("received event '4':", data)
        received_events_4_by_clerk.append(json.loads(data))
        event_4_received_by_clerk.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

        # start

    time.sleep(0.2)
    body = {"SaleID": 1369, "Event": "FINISHED_LOT_TIME",
            "LotID": next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 1)))}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_4_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_4_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_4_by_clerk[0]['Status'] == "SOLD", "sale status is wrong"
    assert received_events_4_by_clerk[0]['MaxBid']['Role'] == "CUSTOMER", "sale status is wrong"
    assert len(received_events_4_by_clerk) > 0, "No events received by clerk"

    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #11 closed", "log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"


def test_group_status_in_related_bids_after_third_biding_on_third_lot(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    lotId = next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 1)))
    Bidname = next((bid['BidName'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 1)))
    body = {
        "SaleID": 1369,
        "UserID": data['login_info']['UserID'],
        "LotID": lotId,
        "BidName": Bidname
    }
    print(body)
    response = relatedBids(body, data['login_info']['GUID'])

    assert response.status_code == 200, "response status code is not 200"
    # assert response.json()['data']['RemainingBudget'] == 1000, "remaining budget is wrong"
    assert response.json()['data']['List'][0]['Status'] == "WON", "status of or bid is wrong!"
    assert response.json()['data']['List'][1]['Status'] == "WON", "status of or bid is wrong!"
    assert response.json()['data']['List'][2]['Status'] == "LOST", "status of or bid is wrong!"
    assert response.json()['data']['List'][3]['Status'] == None, "status of or bid is wrong!"


def test_reopen_third_lot_for_retract(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    received_events_2_by_clerk = []
    event_2_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()
    received_events_3_by_clerk = []
    event_3_received_by_clerk = threading.Event()

    @socket_clerk_client.on('2')
    def event_1(data):
        # print("received event '2':", data)
        received_events_2_by_clerk.append(json.loads(data))
        event_2_received_by_clerk.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

    @socket_clerk_client.on('3')
    def event_1(data):
        # print("received event '3':", data)
        received_events_3_by_clerk.append(json.loads(data))
        event_3_received_by_clerk.set()

        # start

    time.sleep(0.1)
    body = {
        "SaleID": 1369,
        "LotID": next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 1))),
        "MinBid": "100",
        "Event": "SET_MIN_BID_AND_OPEN_LOT"
    }
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_2_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_3_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_2_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_2_by_clerk[0]['Lot']['Status'] == "IN_SALE", "lot status is wrong"
    assert len(received_events_2_by_clerk) > 0, "No events received by clerk"
    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #11 opened at $100", "Log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
    assert event_3_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_3_by_clerk[0]['OpeningBasePrice'] == 100, "opening price is wrong"
    assert len(received_events_3_by_clerk) > 0, "No events received by clerk"


def test_retract_highest_bid_of_online_user(socket_clerk_client):
    first_user_data = json.load(open('fixtures/init_data/first_customer.json'))
    second_user_data = json.load(open('fixtures/init_data/second_customer.json'))
    lotId = next((BID['lotInfo']['LotID'] for BID in second_user_data['bidList'] if BID.get("lot") == (lot_number + 1)))
    # Bidname = next((BID['BidName'] for BID in data['bidList'] if BID.get("lot") == (lot_number + 1)))
    # BidVal = next((BID['bidValue'] for BID in data['bidList'] if BID.get("lot") == (lot_number + 1)))

    received_events_3_by_first_customer = []
    event_3_received_by_first_customer = threading.Event()
    received_events_30_by_first_customer = []
    event_30_received_by_first_customer = threading.Event()
    received_events_33_by_first_customer = []
    event_33_received_by_first_customer = threading.Event()

    @socket_clerk_client.on('33')
    def event_1(data):
        # print("received event '33':", data)
        received_events_33_by_first_customer.append(json.loads(data))
        event_33_received_by_first_customer.set()

    @socket_clerk_client.on('3')
    def event_1(data):
        # print("received event '3':", data)
        received_events_3_by_first_customer.append(json.loads(data))
        event_3_received_by_first_customer.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_first_customer.append(json.loads(data))
        event_30_received_by_first_customer.set()

    time.sleep(3)
    clerk_list_body = {"SaleID": 1369, "LotID": lotId}
    list_res = (clerkList(clerk_list_body, clerk_token)).json()
    if list_res:
        bids = list_res.get("data", {}).get("Bids", [])
        bidID = next((bid["BidID"] for bid in bids if bid.get("UserID") == first_user_data['login_info']['UserID']),
                     None)
    body = {"Live": True, "SaleID": 1369, "LotID": lotId, "BidID": bidID,
            "UserID": first_user_data['login_info']['UserID'],
            "Status": "RETRACT_BY_AUCTIONEER"}
    res = retract(body, clerk_token)
    # Wait for the event to be received or timeout after a certain duration
    event_3_received_by_first_customer.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_first_customer.wait(timeout=5)  # Adjust the timeout value as needed
    event_33_received_by_first_customer.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_33_received_by_first_customer.is_set(), "Event not received by clerk"
    # assert received_events_33_by_first_customer[0]['OpeningBasePrice'] == 5500, "opening base price is wrong"
    assert len(received_events_33_by_first_customer) > 0, "No events received by clerk"

    assert event_3_received_by_first_customer.is_set(), "Event not received by clerk"
    assert received_events_3_by_first_customer[0]['OpeningBasePrice'] == 100, "opening base price is wrong"
    assert len(received_events_3_by_first_customer) > 0, "No events received by clerk"

    assert event_30_received_by_first_customer.is_set(), "Event not received by clerk"
    assert received_events_30_by_first_customer[0]['LogText'] == "Bid $700 retracted", "log text is wrong"
    assert len(received_events_30_by_first_customer) > 0, "No events received by clerk"


def test_close_third_lot_after_retract_highest_bid(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    received_events_4_by_clerk = []
    event_4_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()

    @socket_clerk_client.on('4')
    def event_1(data):
        # print("received event '4':", data)
        received_events_4_by_clerk.append(json.loads(data))
        event_4_received_by_clerk.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

        # start

    time.sleep(0.2)
    body = {"SaleID": 1369, "Event": "FINISHED_LOT_TIME",
            "LotID": next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 1)))}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_4_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_4_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_4_by_clerk[0]['Status'] == "SOLD", "sale status is wrong"
    assert received_events_4_by_clerk[0]['MaxBid']['Role'] == "CUSTOMER", "sale status is wrong"
    assert len(received_events_4_by_clerk) > 0, "No events received by clerk"

    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #11 closed", "log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"


def test_open_forth_lot(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    received_events_2_by_clerk = []
    event_2_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()
    received_events_3_by_clerk = []
    event_3_received_by_clerk = threading.Event()

    @socket_clerk_client.on('2')
    def event_1(data):
        # print("received event '2':", data)
        received_events_2_by_clerk.append(json.loads(data))
        event_2_received_by_clerk.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

    @socket_clerk_client.on('3')
    def event_1(data):
        # print("received event '3':", data)
        received_events_3_by_clerk.append(json.loads(data))
        event_3_received_by_clerk.set()

        # start

    time.sleep(0.1)
    body = {
        "SaleID": 1369,
        "LotID": next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 2))),
        "MinBid": "8500",
        "Event": "SET_MIN_BID_AND_OPEN_LOT"
    }
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_2_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_3_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_2_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_2_by_clerk[0]['Lot']['Status'] == "IN_SALE", "lot status is wrong"
    assert len(received_events_2_by_clerk) > 0, "No events received by clerk"
    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #12 opened at $8,500", "Log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
    assert event_3_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_3_by_clerk[0]['OpeningBasePrice'] == 8500, "opening price is wrong"
    assert len(received_events_3_by_clerk) > 0, "No events received by clerk"


def test_close_last_lot(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    received_events_4_by_clerk = []
    event_4_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()

    @socket_clerk_client.on('4')
    def event_1(data):
        # print("received event '4':", data)
        received_events_4_by_clerk.append(json.loads(data))
        event_4_received_by_clerk.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

        # start

    time.sleep(0.2)
    body = {"SaleID": 1369, "Event": "FINISHED_LOT_TIME",
            "LotID": next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 2)))}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_4_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_4_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_4_by_clerk[0]['Status'] == "NOT_SOLD", "sale status is wrong"
    assert received_events_4_by_clerk[0]['MaxBid']['Role'] == "CLERK", "sale status is wrong"
    assert len(received_events_4_by_clerk) > 0, "No events received by clerk"

    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #12 closed", "log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"


def test_group_status_in_related_bids_after_third_biding_on_forth_lot(socket_clerk_client):
    data = json.load(open('fixtures/init_data/second_customer.json'))
    lotId = next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 1)))
    Bidname = next((bid['BidName'] for bid in data['bidList'] if bid.get("lot") == (lot_number + 1)))
    body = {
        "SaleID": 1369,
        "UserID": data['login_info']['UserID'],
        "LotID": lotId,
        "BidName": Bidname
    }
    print(body)
    response = relatedBids(body, data['login_info']['GUID'])

    assert response.status_code == 200, "response status code is not 200"
    # assert response.json()['data']['RemainingBudget'] == 1000, "remaining budget is wrong"
    assert response.json()['data']['List'][0]['Status'] == "WON", "status of or bid is wrong!"
    assert response.json()['data']['List'][1]['Status'] == "WON", "status of or bid is wrong!"
    assert response.json()['data']['List'][2]['Status'] == "WON", "status of or bid is wrong!"
    assert response.json()['data']['List'][3]['Status'] == "CANCELED", "status of or bid is wrong!"
