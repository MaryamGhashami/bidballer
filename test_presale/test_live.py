import json

import socketio
from services.login import login
from services.auctioneer import start_auction

sio = socketio.Client()


@sio.event
def connect():
    print("I'm connected!")


@sio.event
def connect_error(data):
    print("The connection failed!")


@sio.event
def disconnect():
    print("I'm disconnected!")


def test_start_auction():
    f = json.load(open('fixtures/config.json'))
    username = f['first_user']['username']
    password = f['first_user']['password']
    token = login(username, password)
    body = {
        "SaleID": 3385,
        "Event": "START_AUCTION"
    }
    res = start_auction(body, token)
    # assert res == 200

    # @sio.on('1')
    # def on_message(data):
    #     print("here 0: ", data)
    #     print(data)
    #     pass

    @sio.on('1')
    def event_1(data):
        print("received event '1':", data)
        # assert 1 == 2
        assert data

    @sio.on('0')
    def event_1(data):
        print("received event '0':", data)
        # assert 1 == 2


    token = login("m.ghashamii76@gmail.com", "1234")
    headers = {
        'Authorization': '{}'.format(token),
        'sale': '3385',
        'transport': 'websocket',
        'EIO': '4',
    }
    # assert 5 ==6

    sio.connect('ws://192.168.2.78:8087/socket.io/?Authorization={}&sale=3385'.format(token), headers=headers)
    sio.emit('connection-data', {'connection-data': 'connectionData'})


    sio.disconnect()


def test_iii():

    print("gbdhfj xcmnvhjbn")






