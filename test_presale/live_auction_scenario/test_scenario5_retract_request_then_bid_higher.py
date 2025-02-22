import json
import threading
import time

from services.auctioneer import auctioneer
from services.login import login
from services.bid import bid, retract, request_for_retract
from services.online import clerkList, statistics, lots
from fixtures.socket_clients.fixtures import socket_clerk_client, socket_firstCustomer_client, \
    socket_secondCustomer_client


user1_token = login("m.ghashamii76@gmail.com", "123456")
user2_token = login("sahar@gmail.com", "1234")
clerk_token = login("clerk@gmail.com", "S@1234s")


def test_open_lot_by_clerk(socket_clerk_client):
    received_events_2_by_clerk = []
    event_2_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()

    @socket_clerk_client.on('2')
    def event_1(data):
        # print("received event '2':", data)
        received_events_2_by_clerk.append(json.loads(data))
        event_2_received_by_clerk.set()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '2':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

        # start

    time.sleep(0.2)
    body = {
        "SaleID": 1369,
        "LotID": 400524,
        "MinBid": "8500",
        "Event": "SET_MIN_BID_AND_OPEN_LOT"
    }
    # body = {"SaleID": 1369, "Event": "START_AUCTION"}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_2_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_2_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_2_by_clerk[0]['id'], ""
    assert len(received_events_2_by_clerk) > 0, "No events received by clerk"
    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'], "Lot #5 opened at $8,500"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"


def test_biding_with_2_customers_and_receiving_events_with_customers_and_clerk(socket_clerk_client,
                                                                               socket_firstCustomer_client,
                                                                               socket_secondCustomer_client):
    data = json.load(open('fixtures/config.json'))
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()
    received_events_by_firstCustomer = []
    event_received_by_firstCustomer = threading.Event()
    received_events_by_secondCustomer = []
    event_received_by_secondCustomer = threading.Event()

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

    @socket_secondCustomer_client.on('27')
    def event_1(data):
        # print("received event '27':", data)
        received_events_by_secondCustomer.append(json.loads(data))
        event_received_by_secondCustomer.set()

        # start

    time.sleep(0.2)
    body_bid_user1 = {"SaleID": 1369, "LotID": 400524, "LotNumber": 5, "BidValue": 9000,
                      "PaddleNumber": data['users']['first_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}
    body_bid_user2 = {"SaleID": 1369, "LotID": 400524, "LotNumber": 5, "BidValue": 10000,
                      "PaddleNumber": data['users']['second_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}
    res_1 = bid(body_bid_user1, user1_token)
    res_2 = bid(body_bid_user2, user2_token)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_received_by_firstCustomer.wait(timeout=5)  # Adjust the timeout value as needed
    event_received_by_secondCustomer.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received"
    assert received_events_by_clerk[0]['id'], ""
    assert len(received_events_by_clerk) > 0, "No events received"
    assert event_received_by_firstCustomer.is_set(), "Event not received"
    assert received_events_by_firstCustomer[0]['id'], ""
    assert len(received_events_by_firstCustomer) > 0, "No events received"
    assert event_received_by_secondCustomer.is_set(), "Event not received"
    assert received_events_by_secondCustomer[0]['id'], ""
    assert len(received_events_by_secondCustomer) > 0, "No events received"


def test_retract_request_by_customer(socket_firstCustomer_client):
    received_events_by_first_customer = []
    event_received_by_first_customer = threading.Event()

    @socket_firstCustomer_client.on('27')
    def event_1(data):
        # print("received event '27':", data)
        received_events_by_first_customer.append(json.loads(data))
        event_received_by_first_customer.set()

        # start

    time.sleep(0.2)
    body = {"Live": True, "SaleID": 1369, "LotID": 400524, "Status": "REQUEST_FOR_RETRACT"}
    res = request_for_retract(body, user1_token)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_first_customer.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_first_customer.is_set(), "Event not received by clerk"
    assert received_events_by_first_customer[0]['id'], ""
    assert len(received_events_by_first_customer) > 0, "No events received by clerk"


def test_bid_higher_after_retract_request(socket_firstCustomer_client):
    data = json.load(open('fixtures/config.json'))
    received_events_by_firstCustomer = []
    event_received_by_firstCustomer = threading.Event()

    # event 17 miad bara user
    @socket_firstCustomer_client.on('27')
    def event_1(data):
        # print("received event '27':", data)
        received_events_by_firstCustomer.append(json.loads(data))
        event_received_by_firstCustomer.set()

    time.sleep(0.2)
    body_bid_user1 = {"SaleID": 1369, "LotID": 400524, "LotNumber": 5, "BidValue": 15000,
                      "PaddleNumber": data['users']['first_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}

    res_1 = bid(body_bid_user1, user1_token)

    event_received_by_firstCustomer.wait(timeout=5)

    assert event_received_by_firstCustomer.is_set(), "Event not received"
    assert received_events_by_firstCustomer[0]['id'], ""
    assert len(received_events_by_firstCustomer) > 0, "No events received"


def test_real_price_of_current_lot(socket_clerk_client):
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()

    @socket_clerk_client.on('0')
    def event_1(data):
        # print("received event '0':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

    socket_clerk_client.emit('connection-data', {'connection-data': 'connectionData'})

    event_received_by_clerk.wait(timeout=5)

    # assert 1 == 2
    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_by_clerk[0]['CurrentLot']['RealPrice'] == 10500, "real price is wrong"
    assert len(received_events_by_clerk) > 0, "No events received by clerk"


def test_close_lot_by_clerk_and_determine_the_winner(socket_clerk_client):
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()

    @socket_clerk_client.on('4')
    def event_1(data):
        # print("received event '4':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

    time.sleep(0.2)
    body = {"SaleID": 1369, "Event": "FINISHED_LOT_TIME", "LotID": 400524}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_by_clerk[0]['Status'] == "SOLD", "sale status is wrong"
    assert received_events_by_clerk[0]['MaxBid']['Role'] == "CUSTOMER", "sale status is wrong"
    assert len(received_events_by_clerk) > 0, "No events received by clerk"



def test_how_am_I_doing():
    time.sleep(2)
    data = json.load(open('fixtures/config.json'))
    query = "1369"
    response = statistics(query, user1_token)
    # print(response.json())
    # assert 1 == 2
    assert response.json()['data']['SaleID'] == 1369
    assert response.json()['data']['CountOfLotUserWin'] == "0"
    assert response.json()['data']['CountOfOfferedLotWithUserBid'] == "0"
    assert response.json()['data']['SumOfHammer'] == "0"
    assert response.json()['data']['CountOfLotWithUserBid'] == "6"
    assert response.json()['data']['SumOfBidOnOfferedLot'] == "49000"
    assert response.json()['data']['SumOfHammerInLostLot'] == "24500"
    assert response.json()['data']['PercentOfMoreBidInLostLot'] == "28"



def test_my_bids():
    body = {
        "Page": 0,
        "SaleID": 1369,
        "Size": 300
    }
    response = lots(body, user1_token)
    # print()
    # print(response.json())
    # print(response.json()['data']['lots'])
    # assert 1 == 2
    assert response.json()['data']['lots'][0]['Status'] == "NOT_SOLD"
    assert response.json()['data']['lots'][0]['RealPrice'] == None
    assert response.json()['data']['lots'][1]['Status'] == "SOLD"
    assert response.json()['data']['lots'][1]['YourBid'] == 9000
    assert response.json()['data']['lots'][1]['RealPrice'] == 9500
    assert response.json()['data']['lots'][2]['Status'] == "SOLD"
    assert response.json()['data']['lots'][2]['RealPrice'] == 9500
    assert response.json()['data']['lots'][2]['YourBid'] == 15000
    assert response.json()['data']['lots'][3]['Status'] == "SOLD"
    assert response.json()['data']['lots'][3]['RealPrice'] == 15000
    assert response.json()['data']['lots'][3]['YourBid'] == 10000
    assert response.json()['data']['lots'][4]['Status'] == "SOLD"
    assert response.json()['data']['lots'][4]['RealPrice'] == 10500
    assert response.json()['data']['lots'][4]['YourBid'] == 15000
