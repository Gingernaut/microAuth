import json


async def test_retrieval(test_server):
    res = await sanic_server.get('/account', headers={'Authorization': ''})
    assert res.status == 200


async def test_signup(test_server):
    payload = {
        "emailAddress": "test@example.com",
        "password": "123456"
    }
    res = await sanic_server.post('/signup', data=json.dumps(payload))

    assert res.status == 201
