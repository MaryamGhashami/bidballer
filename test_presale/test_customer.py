import json
import pytest
import requests
from services.login import login
from services.terms import add_paddle, accept_terms
from services.bid import bid


def test_register_user_then_add_paddle():
    with open('fixtures/config.json') as file:
        data = json.load(file)
    for user in ['first_user', 'second_user', 'third_user']:
        username = data['users'][user]['username']
        password = data['users'][user]['password']
        print(username, password)
        token = login(username, password)
        body = {"SaleID": "1369"}
        accept_res = accept_terms(body, token)
        print(accept_res)
        res = add_paddle(body, token)
        paddleNum = res['data']
        print(paddleNum)
        data['users'][user]['paddleNum'] = paddleNum
    with open('fixtures/config.json', 'w') as file:
        json.dump(data, file, indent=2)
    assert 1 == 1
