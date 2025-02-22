import json
import threading
import time
import pytest
from services.login import login
from services.bid import bid, retract
from services.online import clerkList
from services.auctioneer import auctioneer
from fixtures.socket_clients.fixtures import socket_clerk_client, socket_firstCustomer_client, \
    socket_secondCustomer_client

conf = json.load(open('fixtures/config.json'))

user1_token = login("m.ghashamii76@gmail.com", "123456")
user2_token = login("sahar@gmail.com", "1234")
clerk_token = login("clerk@gmail.com", "S@1234s")


# @pytest.mark.arg1("m.ghashami_clerk")
# @pytest.mark.arg2("1234")
def test_event_reception_and_socket_connection_for_clerk(socket_clerk_client):
    received_events = []
    event_received = threading.Event()  # Event to synchronize event reception

    @socket_clerk_client.on('0')
    def handle_event(data):
        # print("Event received:", data)
        received_events.append(json.loads(data))
        event_received.set()  # Signal that the event is received

    # Trigger the event or perform actions that should trigger the event

    # Wait for the event to be received or timeout after a certain duration
    event_received.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received.is_set(), "Event not received"
    assert received_events[0]['CurrentLot']['SaleID'] == 1369, "Incorrect SaleID"
    assert len(received_events) > 0, "No events received"


# @pytest.mark.arg1("m.ghashamii76@gmail.com")
# @pytest.mark.arg2("1234")
def test_event_reception_and_socket_connection_for_first_customer(socket_firstCustomer_client):
    received_events = []
    event_received = threading.Event()  # Event to synchronize event reception

    @socket_firstCustomer_client.on('0')
    def handle_event(data):
        # print("Event received for customer:", data)
        received_events.append(json.loads(data))
        event_received.set()  # Signal that the event is received

    # Trigger the event or perform actions that should trigger the event

    # Wait for the event to be received or timeout after a certain duration
    event_received.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received.is_set(), "Event not received"
    assert received_events[0]['CurrentLot']['SaleID'] == 1369, "Incorrect SaleID"
    assert len(received_events) > 0, "No events received"


# @pytest.mark.arg1("m.ghashamii76@gmail.com")
# @pytest.mark.arg2("1234")
def test_event_reception_and_socket_connection_for_second_customer(socket_secondCustomer_client):
    received_events = []
    event_received = threading.Event()  # Event to synchronize event reception

    @socket_secondCustomer_client.on('0')
    def handle_event(data):
        # print("Event received for customer:", data)
        received_events.append(json.loads(data))
        event_received.set()  # Signal that the event is received

    # Trigger the event or perform actions that should trigger the event

    # Wait for the event to be received or timeout after a certain duration
    event_received.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received.is_set(), "Event not received"
    assert received_events[0]['CurrentLot']['SaleID'] == 1369, "Incorrect SaleID"
    assert len(received_events) > 0, "No events received"


# @pytest.mark.arg1("m.ghashamii76@gmail.com")
# @pytest.mark.arg2("1234")
def test_start_auction_by_clerk(socket_clerk_client, socket_firstCustomer_client):
    received_events_by_customer = []
    received_events_by_clerk = []
    event_received_by_customer = threading.Event()
    event_received_by_clerk = threading.Event()

    @socket_clerk_client.on('1')
    def event_1(data):
        # print("received event '1':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

    @socket_firstCustomer_client.on('1')
    def event_1(data):
        # print("received event '1':", data)
        received_events_by_customer.append(json.loads(data))
        event_received_by_customer.set()

    body = {"SaleID": 1369, "Event": "START_AUCTION"}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_received_by_customer.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_by_clerk[0]['sale']['Status'] == "LIVE", "sale status is wrong"
    assert received_events_by_clerk[0]['sale']['SaleID'] == 1369, "sale status is wrong"
    assert len(received_events_by_clerk) > 0, "No events received by clerk"
    assert event_received_by_customer.is_set(), "Event not received by customer"
    assert received_events_by_customer[0]['sale']['Status'] == "LIVE", "sale status is wrong"
    assert received_events_by_customer[0]['sale']['SaleID'] == 1369, "sale status is wrong"
    assert len(received_events_by_customer) > 0, "No events received by customer"


# @pytest.mark.arg1("m.ghashamii76@gmail.com")
# @pytest.mark.arg2("1234")
def test_open_lot_by_clerk(socket_clerk_client):
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
        "LotID": 400520,
        "MinBid": "5500",
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
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #1 opened at $5,500", "Log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
    assert event_3_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_3_by_clerk[0]['OpeningBasePrice'] == 5500, "opening price is wrong"
    assert len(received_events_3_by_clerk) > 0, "No events received by clerk"


# @pytest.mark.arg1("m.ghashamii76@gmail.com")
# @pytest.mark.arg2("1234")
def test_biding_with_2_customers_and_receiving_events_with_customers_and_clerk(socket_clerk_client,
                                                                               socket_firstCustomer_client,
                                                                               socket_secondCustomer_client):
    data = json.load(open('fixtures/config.json'))
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()
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

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

    body_bid_user1 = {"SaleID": 1369, "LotID": 400520, "LotNumber": 1, "BidValue": 8000,
                      "PaddleNumber": data['users']['first_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}
    body_bid_user2 = {"SaleID": 1369, "LotID": 400520, "LotNumber": 1, "BidValue": 10000,
                      "PaddleNumber": data['users']['second_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}
    res_1 = bid(body_bid_user1, user1_token)
    res_2 = bid(body_bid_user2, user2_token)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_received_by_firstCustomer.wait(timeout=5)  # Adjust the timeout value as needed
    event_received_by_secondCustomer.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received"
    assert received_events_by_clerk[0]['Data']['PaddleNumber'] == data['users']['first_user'][
        'paddleNum'], "the paddle number is wrong"
    assert len(received_events_by_clerk) > 0, "No events received"

    assert event_30_received_by_clerk.is_set(), "Event not received"
    assert received_events_30_by_clerk[0]['LogText'] == "Paddle {} ".format(
        data['users']['first_user']['paddleNum']), "log text is wrong"
    assert received_events_30_by_clerk[0]['RealPrice'] == "5,750", "real price of log is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received"

    assert event_received_by_firstCustomer.is_set(), "Event not received"
    assert received_events_by_firstCustomer[0]['UserID'], ""
    assert received_events_by_firstCustomer[0]['Active'] == "8000", "bid value is wrong"
    assert len(received_events_by_firstCustomer) > 0, "No events received"

    assert event_received_by_secondCustomer.is_set(), "Event not received"
    assert received_events_by_secondCustomer[0]['UserID'], ""
    assert received_events_by_secondCustomer[0]['Active'] == "10000", "bid value is wrong"
    assert len(received_events_by_secondCustomer) > 0, "No events received"


def test_not_to_be_allowed_to_bid_under_MaxBid(socket_firstCustomer_client):
    data = json.load(open('fixtures/config.json'))
    body_bid = {"SaleID": 1369, "LotID": 400520, "LotNumber": 1, "BidValue": 1000,
                "PaddleNumber": data['users']['second_user']['paddleNum'],
                "BidSubmitType": "LIVE"}
    response = bid(body_bid, user1_token)

    assert response.status_code == 923
    assert response.json()["message"] == "Bid value is invalid."


def test_finding_the_winner_befor_retract(socket_clerk_client):
    received_events_by_first_customer = []
    event_received_by_first_customer = threading.Event()

    @socket_clerk_client.on('0')
    def event_1(data):
        # print("received event '0':", data)
        received_events_by_first_customer.append(json.loads(data))
        event_received_by_first_customer.set()

    socket_clerk_client.emit('connection-data', {'connection-data': 'connectionData'})

    event_received_by_first_customer.wait(timeout=5)

    assert event_received_by_first_customer.is_set(), "Event not received by clerk"
    assert received_events_by_first_customer[0]['MaxBid']['BidValue'] == 10000, "MAX bid is wrong"
    assert len(received_events_by_first_customer) > 0, "No events received by clerk"


def test_retract_for_first_winner_customer_by_clerk(socket_clerk_client):
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
    clerk_list_body = {"SaleID": 1369, "LotID": 400520}
    list_res = clerkList(clerk_list_body, clerk_token)
    if list_res:
        bids = list_res.get("data", {}).get("Bids", [])
        bidID = next((bid["BidID"] for bid in bids if bid.get("UserID") == 30848), None)
    body = {"Live": True, "SaleID": 1369, "LotID": 400520, "BidID": bidID, "UserID": 30848,
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
    assert received_events_3_by_first_customer[0]['OpeningBasePrice'] == 5500, "opening base price is wrong"
    assert len(received_events_3_by_first_customer) > 0, "No events received by clerk"

    assert event_30_received_by_first_customer.is_set(), "Event not received by clerk"
    assert received_events_30_by_first_customer[0]['LogText'] == "Bid $10,000 retracted", "log text is wrong"
    assert len(received_events_30_by_first_customer) > 0, "No events received by clerk"


def test_retract_for_second_winner_customer_by_clerk(socket_clerk_client):
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

    clerk_list_body = {"SaleID": 1369, "LotID": 400520}
    list_res = clerkList(clerk_list_body, clerk_token)
    if list_res:
        bids = list_res.get("data", {}).get("Bids", [])
        bidID = next((bid["BidID"] for bid in bids if bid.get("UserID") == 31034), None)
    body = {"Live": True, "SaleID": 1369, "LotID": 400520, "BidID": bidID, "UserID": 31034,
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
    assert received_events_3_by_first_customer[0]['OpeningBasePrice'] == 7500, "opening base price is wrong"
    assert len(received_events_3_by_first_customer) > 0, "No events received by clerk"

    assert event_30_received_by_first_customer.is_set(), "Event not received by clerk"
    assert received_events_30_by_first_customer[0]['LogText'] == "Bid $8,000 retracted", "log text is wrong"
    assert len(received_events_30_by_first_customer) > 0, "No events received by clerk"


def test_finding_the_winner_after_retract(socket_clerk_client):
    received_events_by_first_customer = []
    event_received_by_first_customer = threading.Event()

    @socket_clerk_client.on('0')
    def event_1(data):
        # print("received event '0':", data)
        received_events_by_first_customer.append(json.loads(data))
        event_received_by_first_customer.set()

    socket_clerk_client.emit('connection-data', {'connection-data': 'connectionData'})

    event_received_by_first_customer.wait(timeout=5)

    assert event_received_by_first_customer.is_set(), "Event not received by clerk"
    assert received_events_by_first_customer[0]['MaxBid']['BidValue'] == 5500, "MAX bid is wrong"
    assert len(received_events_by_first_customer) > 0, "No events received by clerk"


# @pytest.mark.arg1("m.ghashamii76@gmail.com")
# @pytest.mark.arg2("1234")
def test_close_lot_by_clerk_and_determine_the_winner(socket_clerk_client):
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

    time.sleep(0.1)
    body = {"SaleID": 1369, "Event": "FINISHED_LOT_TIME", "LotID": 400520}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_4_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed
    event_30_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_4_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_4_by_clerk[0]['Status'] == "NOT_SOLD", "sale status is wrong"
    assert received_events_4_by_clerk[0]['MaxBid']['Role'] == "CLERK", "sale status is wrong"
    assert len(received_events_4_by_clerk) > 0, "No events received by clerk"

    assert event_30_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_30_by_clerk[0]['LogText'] == "Lot #1 closed", "log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
