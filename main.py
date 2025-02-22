import json
import socketio
import bid
from services import login, terms
# from services import

# print(json.dumps({'SaleID': 1369, 'LotID': 400520, 'MinBid': '7500', 'Event': 'SET_MIN_BID_AND_OPEN_LOT'}))

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


@sio.on('*')
def catch_all(event, data):
    print("here_clerk", event, ":", data)
    pass


@sio.event
def message(data):
    print('I received a message!')


token = json.load(open('fixtures/first_clerk.json'))['login_info']['GUID']
headers = {
    'Authorization': '{}'.format(token),
    'sale': '1369',
    'transport': 'websocket',
    'EIO': '4',
}

sio.connect('ws://192.168.2.184:8087/socket.io/?Authorization={}&sale=1369'.format(token), headers=headers)
sio.emit('connection-data', {'connection-data': 'connectionData'})



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


@sio.on('*')
def catch_all(event, data):
    print("here_user", event, ":", data)
    pass


@sio.event
def message(event, data):
    print(event, ":", data)
    print('I received a message!')



token = json.load(open('fixtures/init_data/first_customer.json'))['login_info']['GUID']
headers = {
    'Authorization': '{}'.format(token),
    'sale': '1369',
    'transport': 'websocket',
    'EIO': '4',
}


sio.connect('ws://192.168.2.184:8087/socket.io/?Authorization={}&sale=1369'.format(token), headers=headers)
sio.emit('connection-data', {'connection-data': 'connectionData'})


print("9999999999999999")


# def socket_client(socket):
#     print("-------------------------------------")
#     client = Client()
#     token = login("m.ghashamii76@gmail.com", "1234")
#     headers = {
#         'Authorization': '{}'.format(token),
#         'sale': '3385',
#         'transport': 'websocket',
#         'EIO': '4',
#     }
#     client.connect('ws://192.168.2.78:8087/socket.io/?Authorization={}&sale=3385'.format(token), headers=headers)
#     client.emit('connection-data', {'connection-data': 'connectionData'})
#     # socket.attach(client)
#     # @client.event
#     # def connect():
#     #     print("I'm connected!")
#     #
#     #
#     # @client.event
#     # def connect_error(data):
#     #     print("The connection failed!")
#     #
#     #
#     # @client.event
#     # def disconnect():
#     #     print("I'm disconnected!")
#     #
#     #
#     # @client.on('*')
#     # def catch_all(event, data):
#     #     print("here_user", event, ":", data)
#     #     pass
#     return client
#
#
# def event_reception(socket_client):
#     print("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
#     received_events = []
#
#     @socket_client.event
#     def connect():
#         print("I'm connected!")
#
#     @socket_client.event
#     def connect_error(data):
#         print("The connection failed!")
#
#     @socket_client.event
#     def disconnect():
#         print("I'm disconnected!")
#
#     @socket_client.on('*')
#     def catch_all(event, data):
#         print("here_user", event, ":", data)
#         pass
#
#     @socket_client.on("event_name")
#     def handle_event(data):
#         received_events.append(data)
#
#     # Trigger the events that should be received
#     # ... your test code that triggers events
#
#     # Perform assertions on the received events
#     print("hello")
#     assert len(received_events) == 2, "Expected to receive 2 events"
#     assert received_events[0] == {"key": "value"}, "Incorrect data for the first event"
#     assert received_events[1] == {"key": "another_value"}, "Incorrect data for the second event"
#
# client = socket_client("")
# event_reception(client)
