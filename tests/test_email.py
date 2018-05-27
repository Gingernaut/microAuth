import pytest

import ujson
from tests.conftest import sendgrid_enabled

# Tests are skipped if sengrid api key is not found in .env


@pytest.fixture
async def create_account(test_server):
    payload = {"emailAddress": "test@example.com", "password": "123456"}
    res = await test_server.post("/signup", data=ujson.dumps(payload))
    return await res.json()


class TestValidateSignup:

    @sendgrid_enabled
    async def test_confirm_account(self, test_server, create_account):
        accData = await create_account
        res = await test_server.post(f"/confirm-account/{accData['UUID']}")
        resData = await res.json()

        assert res.status == 200
        assert resData["success"] == "User account confirmed"
        assert resData["isVerified"] == True

    @sendgrid_enabled
    async def test_failed_confirmation(self, test_server):
        res = await test_server.post(f"/confirm-account/abcdefghijk")
        resData = await res.json()

        assert res.status == 400
        assert resData["error"] == "No user for given token"

        # res2 = await test_server.get(
        #     "/account", headers=[("Authorization", accData["jwt"])]
        # )
        # res2Data = await res2.json()

        # assert res2Data["isVerified"] == True


class TestPasswordReset:

    @sendgrid_enabled
    async def test_create_reset(self, test_server, create_account):
        accData = await create_account
        res = await test_server.post(f"/reset-password/{accData['emailAddress']}")
        resData = await res.json()

        assert res.status == 200
        assert resData["message"] == "A reset email has been sent"

    @sendgrid_enabled
    async def test_failed_create_reset(self, test_server):
        res = await test_server.post("/reset-password/does_not_exist@example.com")
        assert res.status == 404

    @sendgrid_enabled
    async def test_valid_reset_token(
        self, test_server, create_account, test_db, test_passreset
    ):

        accData = await create_account
        res = await test_server.post(f"/reset-password/{accData['emailAddress']}")

        reset = (
            test_db.session.query(test_passreset)
            .filter_by(userId=accData["id"])
            .first()
        )

        assert reset.userId == accData["id"]
        assert reset.isValid == True

        res2 = await test_server.post(f"/confirm-reset/{reset.UUID}")
        res2Data = await res2.json()

        assert res2.status == 200
        assert (
            res2Data["message"]
            == "Valid token provided. Prompt user to change password"
        )
        assert "jwt" in res2Data
        assert res2Data["emailAddress"] == accData["emailAddress"]

    @sendgrid_enabled
    async def test_invalid_reset_token(self, test_server):
        res = await test_server.post("/reset-password/does_not_exist")

        assert res.status == 404
