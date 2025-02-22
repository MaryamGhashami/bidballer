import json
import threading
import time

from services.auctioneer import auctioneer
from services.login import login
from services.bid import bid, retract, request_for_retract
from services.online import clerkList
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
        print("received event '2':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

        # start

    time.sleep(0.1)
    body = {
        "SaleID": 1369,
        "LotID": 400521,
        "MinBid": "8500",
        "Event": "SET_MIN_BID_AND_OPEN_LOT"
    }
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_by_clerk[0]['id'], ""
    assert len(received_events_by_clerk) > 0, "No events received by clerk"


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

    time.sleep(0.1)
    body_bid_user1 = {"SaleID": 1369, "LotID": 400521, "LotNumber": 2, "BidValue": 9000,
                      "PaddleNumber": data['users']['first_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}
    body_bid_user2 = {"SaleID": 1369, "LotID": 400521, "LotNumber": 2, "BidValue": 10000,
                      "PaddleNumber": data['users']['second_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}
    body_second_bid_user2 = {"SaleID": 1369, "LotID": 400521, "LotNumber": 2, "BidValue": 110000,
                      "PaddleNumber": data['users']['second_user']['paddleNum'],
                      "BidSubmitType": "LIVE"}
    res_1 = bid(body_bid_user1, user1_token)
    res_2 = bid(body_bid_user2, user2_token)
    res_3 = bid(body_second_bid_user2, user2_token)

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

    # assert 1 == 2
    assert event_received_by_first_customer.is_set(), "Event not received by clerk"
    assert received_events_by_first_customer[0]['MaxBid']['BidValue'] == 10000, "MAX bid is wrong"
    assert len(received_events_by_first_customer) > 0, "No events received by clerk"


def test_retract_request_for_first_customer_by_customer(socket_firstCustomer_client):
    received_events_by_first_customer = []
    event_received_by_first_customer = threading.Event()

    @socket_firstCustomer_client.on('27')
    def event_1(data):
        # print("received event '27':", data)
        received_events_by_first_customer.append(json.loads(data))
        event_received_by_first_customer.set()

        # start

    time.sleep(0.1)
    body = {"Live": True, "SaleID": 1369, "LotID": 400521, "Status": "REQUEST_FOR_RETRACT"}
    res = request_for_retract(body, user1_token)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_first_customer.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_first_customer.is_set(), "Event not received by clerk"
    assert received_events_by_first_customer[0]['id'], ""
    assert len(received_events_by_first_customer) > 0, "No events received by clerk"


def test_retract_request_for_second_customer_by_customer(socket_secondCustomer_client):
    received_events_by_second_customer = []
    event_received_by_second_customer = threading.Event()

    @socket_secondCustomer_client.on('27')
    def event_1(data):
        # print("received event '27':", data)
        received_events_by_second_customer.append(json.loads(data))
        event_received_by_second_customer.set()

        # start

    time.sleep(0.1)
    body = {"Live": True, "SaleID": 1369, "LotID": 400521, "Status": "REQUEST_FOR_RETRACT"}
    res = request_for_retract(body, user2_token)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_second_customer.wait(timeout=5)  # Adjust the timeout value as needed


    assert event_received_by_second_customer.is_set(), "Event not received by clerk"
    assert received_events_by_second_customer[0]['id'], ""
    assert len(received_events_by_second_customer) > 0, "No events received by clerk"


def test_reject_retract_request_by_clerk_for_first_customer(socket_clerk_client):
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()
    # event 17 miad bara user
    @socket_clerk_client.on('3')
    def event_1(data):
        # print("received event '3':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

    clerk_list_body = {"SaleID": 1369, "LotID": 400521}
    list_res = clerkList(clerk_list_body, clerk_token)
    if list_res:
        bids = list_res.get("data", {}).get("Bids", [])
        bidID = next((bid["BidID"] for bid in bids if bid.get("UserID") == 31034), None)

    time.sleep(0.1)
    body = {
        "Live": True,
        "BidID": bidID,
        "LotID": 400521,
        "SaleID": 1369,
        "CurrentBidStatus": "REQUEST_FOR_RETRACT",
        "UserID": 31034,
        "Status": "RETURN_FROM_REQUEST_FOR_RETRACT"
    }
    res = retract(body, clerk_token)

    event_received_by_clerk.wait(timeout=5)

    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    # assert received_events_by_clerk[0]['Status'] == "RETURN_FROM_REQUEST_FOR_RETRACT", "retract status is wrong"
    assert received_events_by_clerk[0]['MaxBid']['BidValue'] == 10000, "bid value is wrong"
    assert received_events_by_clerk[0]['MaxBid']['UserID'] == 30848, "the user is wrong"
    # assert received_events_by_clerk[0]['AdjustValue'] == "RETURN_FROM_REQUEST_FOR_RETRACT", "bid value is wrong"
    assert len(received_events_by_clerk) > 0, "No events received by clerk"


def test_accept_retract_request_by_clerk_for_second_customer(socket_clerk_client):
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()

    # event 17 miad bara user
    @socket_clerk_client.on('3')
    def event_1(data):
        # print("received event '3':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

    clerk_list_body = {"SaleID": 1369, "LotID": 400521}
    list_res = clerkList(clerk_list_body, clerk_token)
    if list_res:
        bids = list_res.get("data", {}).get("Bids", [])
        bidID = next((bid["BidID"] for bid in bids if bid.get("UserID") == 30848), None)

    time.sleep(0.1)
    body = {
        "Live": True,
        "BidID": bidID,
        "LotID": 400521,
        "SaleID": 1369,
        "CurrentBidStatus": "REQUEST_FOR_RETRACT",
        "UserID": 30848,
        "Status": "RETRACT_BY_REQUEST"
    }
    res = retract(body, clerk_token)

    event_received_by_clerk.wait(timeout=5)

    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    # assert received_events_by_clerk[0]['Status'] == "RETURN_FROM_REQUEST_FOR_RETRACT", "retract status is wrong"
    assert received_events_by_clerk[0]['MaxBid']['BidValue'] == 10000, "bid value is wrong"
    assert received_events_by_clerk[0]['MaxBid']['UserID'] == 30848, "the user is wrong"
    # assert received_events_by_clerk[0]['AdjustValue'] == "RETURN_FROM_REQUEST_FOR_RETRACT", "bid value is wrong"
    assert len(received_events_by_clerk) > 0, "No events received by clerk"


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

    # assert 1 == 2
    assert event_received_by_first_customer.is_set(), "Event not received by clerk"
    assert received_events_by_first_customer[0]['MaxBid']['BidValue'] == 10000, "MAX bid is wrong"
    assert len(received_events_by_first_customer) > 0, "No events received by clerk"


def test_close_lot_by_clerk_and_determine_the_winner(socket_clerk_client):
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()

    @socket_clerk_client.on('4')
    def event_1(data):
        # print("received event '4':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

        # start
    time.sleep(0.1)
    body = {"SaleID": 1369, "Event": "FINISHED_LOT_TIME", "LotID": 400521}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_by_clerk[0]['Status'] == "SOLD", "sale status is wrong"
    assert received_events_by_clerk[0]['MaxBid']['Role'] == "CUSTOMER", "sale status is wrong"
    assert len(received_events_by_clerk) > 0, "No events received by clerk"



