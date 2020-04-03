import pytest
import ujson

from models.reset import PasswordReset


@pytest.fixture
def create_account(test_server):
    payload = {"emailAddress": "test123@example.com", "password": "123456"}
    res = test_server.post("/signup", data=ujson.dumps(payload))
    return res.json()


class TestValidateSignup:
    def test_confirm_account(self, test_server, create_account, db_session):
        accData = create_account

        reset = (
            db_session.query(PasswordReset)
            .filter(PasswordReset.userId == accData["id"])
            .first()
        )
        print("!!!")
        print(accData)
        print(reset)
        print("!!!")

        confirmResponse = test_server.post(f"/confirm-account/{reset.gen_token()}")

        assert confirmResponse.status_code == 200
        assert confirmResponse.json()["isVerified"] is True

    def test_failed_confirmation(self, test_server):
        res = test_server.post(f"/confirm-account/abcdefghijk")
        print("!!!")
        print(res.json())
        print("!!!")
        assert res.status_code == 403


class TestPasswordReset:
    def test_create_reset(self, test_server, create_account):
        accData = create_account
        res = test_server.post(f"/initiate-reset/{accData['emailAddress']}")
        print("!!!")
        print(accData)
        print(res.json())
        print("!!!")
        assert res.status_code == 200

        def test_failed_create_reset(self, test_server):
            res = test_server.post("/initiate-reset/does_not_exist@example.com")
            assert res.status_code == 404

    def test_valid_reset_token(self, test_server, create_account, db_session):

        accData = create_account
        test_server.post(f"/initiate-reset/{accData['emailAddress']}")

        reset = db_session.query(PasswordReset).filter_by(userId=accData["id"]).first()

        print("!!!")
        print(accData)
        print(reset)
        print("!!!")

        assert reset.userId == accData["id"]
        assert reset.isValid is True

        res2 = test_server.post(f"/confirm-reset/{reset.gen_token()}")
        res2Data = res2.json()

        assert res2.status_code == 200
        assert "jwt" in res2Data
        assert res2Data["emailAddress"] == accData["emailAddress"]

    def test_invalid_reset_token(self, test_server):
        res = test_server.post("/initiate-reset/does_not_exist")

        assert res.status_code == 404
