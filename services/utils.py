from socketio import Client
from services.login import login


# def bid_body(customer, bid):
#     return {
#         "SaleID":
#     }


# def socket_client(request):
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
#     def close_client():
#         client.disconnect()
#
#     request.addfinalizer(close_client())
#     return client

def find_item_by_name(json_list, key, value):
    for json_obj in json_list:
        if json_obj["{}".format(key)] == value:
            return True
    return False


def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def searchBody(searchItem, lotnumber=None):
    return {
        "SaleID": "1369",
        "LotNumber": lotnumber,
        "MyBids": searchItem
    }


def adjValue(remaining, bidvalue):
    if remaining >= bidvalue:
        adj = bidvalue
    else:
        adj = remaining
    return adj
