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

lot_number = 6
user1_token = json.load(open('fixtures/init_data/first_customer.json'))['login_info']['GUID']
# user2_token = json.load(open('fixtures/init_data/second_customer.json'))['login_info']['GUID']
clerk_token = json.load(open('fixtures/first_clerk.json'))['login_info']['GUID']


def test_or_status_in_related_bids(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
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
    assert response.json()['data']['List'][0]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][1]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][2]['Status'] == None, "status of or bid is wrong!"


def test_open_lot_by_clerk(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
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
        "MinBid": "200",
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
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #6 opened at $200", "Log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
    assert event_3_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_3_by_clerk[0]['OpeningBasePrice'] == 200, "opening price is wrong"
    assert len(received_events_3_by_clerk) > 0, "No events received by clerk"


def test_close_lot_by_clerk_and_determine_the_winner(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
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
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #6 closed", "log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"


def test_or_status_in_related_bids_after_winnig_first_one(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
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
    assert response.json()['data']['List'][0]['Status'] == "WON", "status of or bid is wrong!"
    assert response.json()['data']['List'][1]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][2]['Status'] == None, "status of or bid is wrong!"


def test_reopen_lot_with_increasing_opening_price(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
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
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #6 opened at $2,000", "Log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
    assert event_3_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_3_by_clerk[0]['OpeningBasePrice'] == 2000, "opening price is wrong"
    assert len(received_events_3_by_clerk) > 0, "No events received by clerk"


def test_or_status_in_related_bids_after_reopening_lot_with_higher_opening_price(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
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
    assert response.json()['data']['List'][0]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][1]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][2]['Status'] == None, "status of or bid is wrong!"


def test_close_lot_again_by_clerk_and_determine_the_winner(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
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
    print("--------------------------", res.status_code)
    print(res.json())

    # Wait for the event to be received or timeout after a certain duration
    event_4_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_4_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_4_by_clerk[0]['Status'] == "NOT_SOLD", "sale status is wrong"
    assert received_events_4_by_clerk[0]['MaxBid']['Role'] == "CLERK", "sale status is wrong"
    assert len(received_events_4_by_clerk) > 0, "No events received by clerk"

    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #6 closed", "log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"


def test_or_status_in_related_bids_after_loosing_first_one(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
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
    assert response.json()['data']['List'][0]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][1]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][2]['Status'] == None, "status of or bid is wrong!"


def test_open_next_lot_by_clerk(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
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
        "MinBid": "10",
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
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #7 opened at $10", "Log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
    assert event_3_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_3_by_clerk[0]['OpeningBasePrice'] == 10, "opening price is wrong"
    assert len(received_events_3_by_clerk) > 0, "No events received by clerk"


def test_or_status_in_related_bids_after_opening_next_lot(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
    lotId = next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number)))
    Bidname = next((bid['BidName'] for bid in data['bidList'] if bid.get("lot") == (lot_number)))
    body = {
        "SaleID": 1369,
        "UserID": data['login_info']['UserID'],
        "LotID": lotId,
        "BidName": Bidname
    }
    print(body)
    response = relatedBids(body, data['login_info']['GUID'])

    assert response.status_code == 200, "response status code is not 200"
    assert response.json()['data']['List'][0]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][1]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][2]['Status'] == None, "status of or bid is wrong!"


def test_close_next_lot_by_clerk_and_determine_the_winner(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
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
    print("--------------------------", res.status_code)
    print(res.json())

    # Wait for the event to be received or timeout after a certain duration
    event_4_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_4_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_4_by_clerk[0]['Status'] == "SOLD", "sale status is wrong"
    assert received_events_4_by_clerk[0]['MaxBid']['Role'] == "CUSTOMER", "sale status is wrong"
    assert len(received_events_4_by_clerk) > 0, "No events received by clerk"

    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #7 closed", "log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"


def test_or_status_in_related_bids_after_closing_next_lot(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
    lotId = next((bid['lotInfo']['LotID'] for bid in data['bidList'] if bid.get("lot") == (lot_number)))
    Bidname = next((bid['BidName'] for bid in data['bidList'] if bid.get("lot") == (lot_number)))
    body = {
        "SaleID": 1369,
        "UserID": data['login_info']['UserID'],
        "LotID": lotId,
        "BidName": Bidname
    }
    print(body)
    response = relatedBids(body, data['login_info']['GUID'])

    assert response.status_code == 200, "response status code is not 200"
    assert response.json()['data']['List'][0]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][1]['Status'] == "WON", "status of or bid is wrong!"
    assert response.json()['data']['List'][2]['Status'] == None, "status of or bid is wrong!"


def test_open_last_lot_of_or_bids(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
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
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #8 opened at $100", "Log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
    assert event_3_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_3_by_clerk[0]['OpeningBasePrice'] == 100, "opening price is wrong"
    assert len(received_events_3_by_clerk) > 0, "No events received by clerk"


def test_or_status_in_related_bids_after_opening_last_lot(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
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
    assert response.json()['data']['List'][0]['Status'] == None, "status of or bid is wrong!"
    assert response.json()['data']['List'][1]['Status'] == "WON", "status of or bid is wrong!"
    assert response.json()['data']['List'][2]['Status'] == "CANCELED", "status of or bid is wrong!"


def test_close_last_lot_by_clerk_and_determine_the_winner(socket_clerk_client):
    data = json.load(open('fixtures/init_data/first_customer.json'))
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
    print("--------------------------", res.status_code)
    print(res.json())

    # Wait for the event to be received or timeout after a certain duration
    event_4_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_4_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_4_by_clerk[0]['Status'] == "SOLD", "sale status is wrong"
    assert received_events_4_by_clerk[0]['MaxBid']['Role'] == "CUSTOMER", "sale status is wrong"
    assert len(received_events_4_by_clerk) > 0, "No events received by clerk"

    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #7 closed", "log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
