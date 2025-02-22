import json
import threading
import time

from services.auctioneer import auctioneer
from services.login import login
from services.bid import bid, retract, request_for_retract
from services.online import clerkList, nextprev
from fixtures.socket_clients.fixtures import socket_clerk_client, socket_firstCustomer_client, \
    socket_secondCustomer_client

user1_token = login("m.ghashamii76@gmail.com", "123456")
user2_token = login("sahar@gmail.com", "1234")
clerk_token = login("clerk@gmail.com", "S@1234s")


# @pytest.mark.arg1("m.ghashamii76@gmail.com")
# @pytest.mark.arg2("1234")
def test_go_to_lot_15():
    body = {
        "SaleID": 1369,
        "LotNumber": "15",
        "Side": 0,
    }
    res = nextprev(body, clerk_token)
    print("77777777777777", res['data']['lot']['Status'])
    print("77777777777777", res['data']['lot']['LotNumber'])

    assert res['data']['lot']['Status'] == "NOT_STARTED", "sale status is wrong"
    assert res['data']['lot']['LotNumber'] == "15", "lot number is wrong"
    assert res['success'] == True, "next prev is failed"


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
        "LotID": 400297,
        "MinBid": "1000",
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
    # assert received_events_30_by_clerk[0]['LogText'] == "Lot #1 opened at $1,000", "Log text is wrong"
    assert len(received_events_30_by_clerk) > 0, "No events received by clerk"
    assert event_3_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_3_by_clerk[0]['OpeningBasePrice'] == 1000, "opening price is wrong"
    assert len(received_events_3_by_clerk) > 0, "No events received by clerk"


def test_pause_Auction(socket_clerk_client, socket_firstCustomer_client):
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()
    received_events_by_customer = []
    event_received_by_customer = threading.Event()

    @socket_clerk_client.on('6')
    def event_1(data):
        # print("received event '6':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

    @socket_firstCustomer_client.on('6')
    def event_1(data):
        # print("received event '6':", data)
        received_events_by_customer.append(json.loads(data))
        event_received_by_customer.set()

    time.sleep(0.3)
    body = {
        "Event": "PAUSE_LOT",
        "LotID": 400297,
        "Paused": True,
        "SaleID": 1369
    }

    response = auctioneer(body, clerk_token)
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    assert len(received_events_by_customer) > 0, "No events received by clerk"
    assert received_events_by_customer[0]["Paused"], "the auction has not been paused"


def test_continue_auction_after_pause(socket_clerk_client, socket_firstCustomer_client):
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()
    received_events_by_customer = []
    event_received_by_customer = threading.Event()

    @socket_clerk_client.on('6')
    def event_1(data):
        # print("received event '6':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

    @socket_firstCustomer_client.on('6')
    def event_1(data):
        # print("received event '6':", data)
        received_events_by_customer.append(json.loads(data))
        event_received_by_customer.set()

    time.sleep(0.3)
    body = {
        "Event": "PAUSE_LOT",
        "LotID": 400297,
        "Paused": False,
        "SaleID": 1369
    }

    response = auctioneer(body, clerk_token)
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    assert len(received_events_by_customer) > 0, "No events received by clerk"
    assert received_events_by_customer[0]["Paused"] == False, "the auction has not been continued"


def test_pass_lot(socket_clerk_client, socket_firstCustomer_client):
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()
    received_events_by_customer = []
    event_received_by_customer = threading.Event()
    received_events_30_by_clerk = []
    event_30_received_by_clerk = threading.Event()

    @socket_clerk_client.on('30')
    def event_1(data):
        # print("received event '30':", data)
        received_events_30_by_clerk.append(json.loads(data))
        event_30_received_by_clerk.set()

    @socket_clerk_client.on('2')
    def event_1(data):
        # print("received event '2':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

    @socket_firstCustomer_client.on('2')
    def event_1(data):
        # print("received event '2':", data)
        received_events_by_customer.append(json.loads(data))
        event_received_by_customer.set()

    time.sleep(0.1)
    body = {
        "Event": "PASS",
        "LotID": 400297,
        "SaleID": 1369
    }
    response = auctioneer(body, clerk_token)
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_by_customer[0]['Lot']['LotNumber'] == "16", "lot number after pass is wrong"
    # assert received_events_30_by_clerk[0]['LogText'] == "Lot #15 passed", "log text message is wrong"
    assert len(received_events_by_customer) > 0, "No events received by clerk"


def test_reopen_lot_4(socket_clerk_client):
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
        "LotID": 400523,
        "Event": "REOPEN_LOT"
    }
    # body = {"SaleID": 1369, "Event": "START_AUCTION"}
    res = auctioneer(body, clerk_token)
    # print("+++++++++++++++++++++++++", res)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_by_clerk[0]['id'], ""
    assert len(received_events_by_clerk) > 0, "No events received by clerk"


def test_compare_all_data_with_last_state_of_lot(socket_clerk_client):
    received_events_by_clerk = []
    event_received_by_clerk = threading.Event()

    @socket_clerk_client.on('0')
    def event_1(data):
        # print("received event '0':", data)
        received_events_by_clerk.append(json.loads(data))
        event_received_by_clerk.set()

    socket_clerk_client.emit('connection-data', {'connection-data': 'connectionData'})

    event_received_by_clerk.wait(timeout=5)

    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_by_clerk[0]['CurrentLot']['LotNumber'] == "4", "lot number is wrong"
    assert received_events_by_clerk[0]['CurrentLot']['OpeningPrice'] == 8500, "opening price is wrong"
    assert received_events_by_clerk[0]['CurrentLot']['RealPrice'] == 15000, "real price is wrong"
    assert received_events_by_clerk[0]['BasePrice'] == 15000, "base price is wrong"
    assert received_events_by_clerk[0]['MaxBid']['BidSubmitType'] == "PHONE", "bid type is wrong"
    assert received_events_by_clerk[0]['MaxBid']['Role'] == "CLERK", "max bid role is wrong"
    assert received_events_by_clerk[0]['MaxBid']['BidValue'] == 15000, "max bid value is wrong"
    assert received_events_by_clerk[0]['UnderBid']['Role'] == "CUSTOMER", "under bid role is wrong"
    assert len(received_events_by_clerk) > 0, "No events received by clerk"


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
    body = {"SaleID": 1369, "Event": "FINISHED_LOT_TIME", "LotID": 400523}
    res = auctioneer(body, clerk_token)

    # Wait for the event to be received or timeout after a certain duration
    event_received_by_clerk.wait(timeout=5)  # Adjust the timeout value as needed

    assert event_received_by_clerk.is_set(), "Event not received by clerk"
    assert received_events_by_clerk[0]['Status'] == "SOLD", "sale status is wrong"
    assert received_events_by_clerk[0]['MaxBid']['Role'] == "CLERK", "sale status is wrong"
    assert len(received_events_by_clerk) > 0, "No events received by clerk"
