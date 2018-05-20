import pytest

import ujson


class TestValidateSignup:

    @pytest.fixture
    async def create_account(self, test_server):
        payload = {"emailAddress": "test@example.com", "password": "123456"}
        res = await test_server.post("/signup", data=ujson.dumps(payload))
        return await res.json()

    async def test_confirm_account(self, test_server, create_account):
        accData = await create_account
        res = await test_server.post(f"/confirm-account/{accData['UUID']}")
        resData = await res.json()

        assert res.status == 200
        assert resData["success"] == "User account confirmed"

        res2 = await test_server.get(
            "/account", headers=[("Authorization", accData["jwt"])]
        )
        resData2 = await res2.json()

        assert resData2["isValidated"] == True


class TestPasswordReset:

    async def test_create_reset(self, test_server, create_account):
        accData = await create_account
        res = await test_server.post(f"/reset-password/{accData['emailAddress']}")
        resData = await res.json()

        assert res.status == 200
        assert resData["message"] == "A reset email has been sent"
