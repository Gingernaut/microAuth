import ujson


# async def test_retrieval(test_server):
#     res = await test_server.get('/account', headers=[('Authorization', '')])
#     assert res.status == 200


async def test_workflow(test_server):
    payload = {
        "emailAddress": "test@example.com",
        "password": "123456"
    }
    res = await test_server.post('/signup', data=ujson.dumps(payload))

    assert res.status == 201
