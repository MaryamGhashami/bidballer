import json

import pytest
from socketio import Client
from services.login import login
conf = json.load(open('fixtures/config.json'))

@pytest.fixture
def socket_firstCustomer_client(request):
    client = Client()
    # arg1 = request.node.get_closest_marker("arg1").args[0]
    # arg2 = request.node.get_closest_marker("arg2").args[0]
    # token = login(arg1, arg2)
    first_user_token = login(conf['users']['first_user']['username'], conf['users']['first_user']['password'], 'first_user')
    headers = {
        'Authorization': '{}'.format(first_user_token),
        'sale': '1369',
        'transport': 'websocket',
        'EIO': '4',
    }
    client.connect('ws://192.168.2.184:8087/socket.io/?Authorization={}&sale=1369'.format(first_user_token),
                   headers=headers)
    client.emit('connection-data', {'connection-data': 'connectionData'})

    # def close_socket_client():
    #     client.disconnect()
    # request.addfinalizer(close_socket_client)

    @client.event
    def connect():
        print("I'm connected!")

    @client.event
    def connect_error(data):
        print("The connection failed!")

    @client.event
    def disconnect():
        print("I'm disconnected!")

    return client


@pytest.fixture
def socket_secondCustomer_client(request):
    client = Client()
    # arg1 = request.node.get_closest_marker("arg1").args[0]
    # arg2 = request.node.get_closest_marker("arg2").args[0]
    # token = login(arg1, arg2)
    second_user_token = login(conf['users']['second_user']['username'], conf['users']['second_user']['password'], 'second_user')
    headers = {
        'Authorization': '{}'.format(second_user_token),
        'sale': '1369',
        'transport': 'websocket',
        'EIO': '4',
    }
    client.connect('ws://192.168.2.184:8087/socket.io/?Authorization={}&sale=1369'.format(second_user_token),
                   headers=headers)
    client.emit('connection-data', {'connection-data': 'connectionData'})

    # def close_socket_client():
    #     client.disconnect()
    # request.addfinalizer(close_socket_client)

    @client.event
    def connect():
        print("I'm connected!")

    @client.event
    def connect_error(data):
        print("The connection failed!")

    @client.event
    def disconnect():
        print("I'm disconnected!")

    return client


@pytest.fixture
def socket_thirdCustomer_client(request):
    client = Client()
    # arg1 = request.node.get_closest_marker("arg1").args[0]
    # arg2 = request.node.get_closest_marker("arg2").args[0]
    # token = login(arg1, arg2)
    third_user_token = login(conf['users']['third_user']['username'], conf['users']['third_user']['password'], 'third_user')
    headers = {
        'Authorization': '{}'.format(third_user_token),
        'sale': '1369',
        'transport': 'websocket',
        'EIO': '4',
    }
    client.connect('ws://192.168.2.184:8087/socket.io/?Authorization={}&sale=1369'.format(third_user_token),
                   headers=headers)
    client.emit('connection-data', {'connection-data': 'connectionData'})

    # def close_socket_client():
    #     client.disconnect()
    # request.addfinalizer(close_socket_client)

    @client.event
    def connect():
        print("I'm connected!")

    @client.event
    def connect_error(data):
        print("The connection failed!")

    @client.event
    def disconnect():
        print("I'm disconnected!")

    return client


@pytest.fixture
def socket_clerk_client(request):
    client = Client()
    # arg1 = request.node.get_closest_marker("arg1").args[0]
    # arg2 = request.node.get_closest_marker("arg2").args[0]
    # token = login(arg1, arg2)
    clerk_token = login(conf['users']['first_clerk']['username'], conf['users']['first_clerk']['password'], 'first_clerk')
    headers = {
        'Authorization': '{}'.format(clerk_token),
        'sale': '1369',
        'transport': 'websocket',
        'EIO': '4',
    }
    client.connect('ws://192.168.2.184:8087/socket.io/?Authorization={}&sale=1369'.format(clerk_token), headers=headers)
    client.emit('connection-data', {'connection-data': 'connectionData'})

    # def close_socket_client():
    #     client.disconnect()
    # request.addfinalizer(close_socket_client)

    @client.event
    def connect():
        print("I'm connected!")

    @client.event
    def connect_error(data):
        print("The connection failed!")

    @client.event
    def disconnect():
        print("I'm disconnected!")

    return client
