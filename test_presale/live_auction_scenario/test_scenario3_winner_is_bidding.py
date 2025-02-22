import json
import threading
import time

from services.auctioneer import auctioneer
from services.login import login
from services.utils import find_item_by_name
from services.bid import bid, retract, request_for_retract
from services.user import bidders
from services.online import lastSoldLot
from services.sale import saleInfo
from fixtures.socket_clients.fixtures import socket_clerk_client, socket_firstCustomer_client, \
    socket_secondCustomer_client

user1_token = login("m.ghashamii76@gmail.com", "123456")
user2_token = login("sahar@gmail.com", "1234")
clerk_token = login("clerk@gmail.com", "S@1234s")


# @pytest.mark.arg1("m.ghashamii76@gmail.com")
# @pytest.mark.arg2("1234")
def test_open_lot_by_clerk(socket_clerk_client):
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()

    @socket_clerk_client.on('2')
    def event_1(data):
        # print("received event '2':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

        # start

    time.sleep(0.1)
    body = {
        "SaleID": 1369,
        "LotID": 400522,
        "MinBid": "8500",
        "Event": "SET_MIN_BID_AND_OPEN_LOT"
    }
    # body = {"SaleID": 1369, "Event": "START_AUCTION"}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_by_clerk[0]['id'], ""
    assert len(received_events_by_clerk) > 0, "No events received by clerk"


def test_biding_with_customer_and_receiving_events_with_customer_and_clerk(socket_clerk_client,
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

    time.sleep(0.5)
    body_bid_user1 = {"SaleID": 1369, "LotID": 400522, "LotNumber": 3, "BidValue": 10000,
                      "PaddleNumber": data['users']['first_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}
    body_bid_user2 = {"SaleID": 1369, "LotID": 400522, "LotNumber": 3, "BidValue": 9000,
                      "PaddleNumber": data['users']['second_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}

    res_2 = bid(body_bid_user2, user2_token)
    res_1 = bid(body_bid_user1, user1_token)

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
    assert received_events_by_clerk[0]['CurrentLot']['RealPrice'] == 9500, "real price is wrong"
    assert len(received_events_by_clerk) > 0, "No events received by clerk"


def test_biding_with_winner_higher_bid(socket_firstCustomer_client):
    data = json.load(open('fixtures/config.json'))
    received_events_by_firstCustomer = []
    event_received_by_firstCustomer = threading.Event()

    @socket_firstCustomer_client.on('27')
    def event_1(data):
        # print("received event '27':", data)
        received_events_by_firstCustomer.append(json.loads(data))
        event_received_by_firstCustomer.set()

        # start

    time.sleep(0.1)
    body_bid_user1 = {"SaleID": 1369, "LotID": 400522, "LotNumber": 3, "BidValue": 15000,
                      "PaddleNumber": data['users']['first_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}
    # body = {"SaleID": 1369, "Event": "START_AUCTION"}
    res_1 = bid(body_bid_user1, user1_token)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_firstCustomer.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_firstCustomer.is_set(), "Event not received by clerk"
    assert received_events_by_firstCustomer[0]['id'], ""
    assert len(received_events_by_firstCustomer) > 0, "No events received by clerk"


def test_close_lot_by_clerk_and_determine_the_winner(socket_clerk_client):
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()

    @socket_clerk_client.on('4')
    def event_1(data):
        print("received event '4':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

        # start

    time.sleep(0.1)
    body = {"SaleID": 1369, "Event": "FINISHED_LOT_TIME", "LotID": 400522}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_by_clerk[0]['Status'] == "SOLD", "sale status is wrong"
    assert received_events_by_clerk[0]['RealPrice'] == 9500, "real price is wrong"
    # assert received_events_by_clerk[0]['MaxBid']['Role'] == "CUSTOMER", "sale status is wrong"
    assert len(received_events_by_clerk) > 0, "No events received by clerk"


def test_last_sold_lot():
    data = json.load(open('fixtures/config.json'))
    query = "1369"
    response = lastSoldLot(query, clerk_token)
    assert response.json()['data']['LotNumber'] == "3", "Lot number of last sold lot is wrong"
    assert response.json()['data']['PaddleNumber'] == data['users']['first_user']['paddleNum'], "paddle number of last sold lot is wrong"
    assert response.json()['data']['RealPrice'] == 9500, "the Price if last sold lot is wrong"


def test_connection_info():
    query = "1369"
    response = saleInfo(query,clerk_token)
    assert response.json()['data']['CountOfDisconnectedUser'] == 0, "count of disconnected users in connection info is wrong"
    assert response.json()['data']['CountOfClerk'] == 1, "count of connected clerks in connection info is wrong"
    assert response.json()['data']['CountOfCustomer'] == 2, "count of connected customers in connection info is wrong"
    assert response.json()['data']['CountOfOnlineUser'] == 3, "count of online users in connection info is wrong"


def test_registered_bidders():
    data = json.load(open('fixtures/config.json'))
    bid_body = {"SaleID": 1369}
    response = bidders(bid_body, clerk_token)
    assert len(response.json()['data']) == len(data['users']), "count of registered users is wrong"
    assert find_item_by_name(response.json()['data'], 'UserName', data['users']['first_user']['username']), "{} is not find in registered users!".format(data['users']['first_user']['username'])
    assert find_item_by_name(response.json()['data'], 'UserName', data['users']['second_user']['username']), "{} is not find in registered users!".format(data['users']['second_user']['username'])
    assert find_item_by_name(response.json()['data'], 'UserName', data['users']['third_user']['username']), "{} is not find in registered users!".format(data['users']['third_user']['username'])
