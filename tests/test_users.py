import pytest

import ujson


@pytest.fixture
async def create_account_jwt(test_server):
    payload = {"emailAddress": "test@example.com", "password": "123456"}
    res = await test_server.post("/signup", data=ujson.dumps(payload))
    resData = await res.json()
    return resData["jwt"]


class TestSignup:

    async def test_valid_signup(self, test_server):
        payload = {"emailAddress": "test@example.com", "password": "123456"}
        res = await test_server.post("/signup", data=ujson.dumps(payload))
        resData = await res.json()

        assert res.status == 201
        assert "jwt" in resData
        assert resData["emailAddress"] == "test@example.com"
        assert resData["userRole"] == "USER"

    async def test_short_pass(self, test_server, app_config):
        payload = {
            "emailAddress": "test@example.com",
            "password": "x" * (app_config.MIN_PASS_LENGTH - 1),
        }

        res = await test_server.post("/signup", data=ujson.dumps(payload))
        resData = await res.json()

        assert res.status == 400
        assert resData["error"] == "Password does not meet required length requirements"

    async def test_missing_pass(self, test_server):
        payload = {"emailAddress": "test@example.com"}
        res = await test_server.post("/signup", data=ujson.dumps(payload))
        resData = await res.json()

        assert res.status == 400
        assert resData["error"] == "No password provided"

    async def test_missing_email(self, test_server):
        payload = {"password": "asdfdfasdfas"}
        res = await test_server.post("/signup", data=ujson.dumps(payload))
        resData = await res.json()

        assert res.status == 400
        assert resData["error"] == "No email address provided"

    async def test_double_signup(self, test_server):
        payload = {"emailAddress": "test@example.com", "password": "123456"}
        res = await test_server.post("/signup", data=ujson.dumps(payload))
        assert res.status == 201

        res2 = await test_server.post("/signup", data=ujson.dumps(payload))
        res2Data = await res2.json()

        assert res2.status == 400
        assert res2Data["error"] == "An account with that email address already exists"


class TestLogin:

    async def test_login(self, test_server, create_account_jwt):
        # creates a "test@example.com" account
        unusedJwt = await create_account_jwt

        payload = {"emailAddress": "test@example.com", "password": "123456"}

        res = await test_server.post("/login", data=ujson.dumps(payload))
        resData = await res.json()

        assert res.status == 200
        assert resData["emailAddress"] == "test@example.com"
        assert "jwt" in resData

    async def test_invalid_password(self, test_server, create_account_jwt):
        # creates a "test@example.com" account
        unusedJwt = await create_account_jwt

        payload = {"emailAddress": "test@example.com", "password": "incorrect_password"}

        res = await test_server.post("/login", data=ujson.dumps(payload))
        resData = await res.json()

        assert res.status == 400
        assert resData["error"] == "Invalid credentials"

    async def test_invalid_email(self, test_server, create_account_jwt):
        # creates a "test@example.com" account
        unusedJwt = await create_account_jwt

        payload = {"emailAddress": "not_an_account@example.com", "password": "123456"}

        res = await test_server.post("/login", data=ujson.dumps(payload))
        resData = await res.json()

        assert res.status == 400
        assert resData["error"] == "No account for provided email address"


class TestAccount:

    async def test_get_account_without_auth(self, test_server):
        res = await test_server.get("/account")
        assert res.status == 401

    async def test_get_info(self, test_server, create_account_jwt):
        jwtToken = await create_account_jwt
        res = await test_server.get("/account", headers=[("Authorization", jwtToken)])
        resData = await res.json()

        assert res.status == 200
        assert "jwt" not in resData
        assert resData["emailAddress"] == "test@example.com"
        assert resData["userRole"] == "USER"
        assert resData["isValidated"] == False

    async def test_valid_update(self, test_server, create_account_jwt):
        jwtToken = await create_account_jwt
        payload = {"firstName": "jason", "lastName": "bourne", "emailAddress": ""}
        res = await test_server.put(
            "/account", headers=[("Authorization", jwtToken)], data=ujson.dumps(payload)
        )
        resData = await res.json()

        assert res.status == 200
        assert resData["success"] == "Account updated"
        assert resData["firstName"] == "Jason"
        assert resData["lastName"] == "Bourne"
        assert resData["emailAddress"] == "test@example.com"

    async def test_update_own_role(self, test_server, create_account_jwt):
        jwtToken = await create_account_jwt
        payload = {"userRole": "ADMIN"}
        res = await test_server.put(
            "/account", headers=[("Authorization", jwtToken)], data=ujson.dumps(payload)
        )
        resData = await res.json()

        assert res.status == 401
        assert resData["error"] == "Unauthorized to update role"

    async def test_update_password(self, test_server, create_account_jwt):
        jwtToken = await create_account_jwt
        payload = {"password": "super_much_secure"}
        res = await test_server.put(
            "/account", headers=[("Authorization", jwtToken)], data=ujson.dumps(payload)
        )
        resData = await res.json()

        assert res.status == 200
        assert resData["success"] == "Account updated"

        login_data = {
            "emailAddress": resData["emailAddress"],
            "password": "super_much_secure",
        }

        login_res = await test_server.post("/login", data=ujson.dumps(login_data))
        login_resData = await login_res.json()

        assert login_res.status == 200
        assert login_resData["emailAddress"] == resData["emailAddress"]

    async def test_short_pass_update(self, test_server, create_account_jwt, app_config):
        jwtToken = await create_account_jwt
        payload = {"password": "x" * (app_config.MIN_PASS_LENGTH - 1)}
        res = await test_server.put(
            "/account", headers=[("Authorization", jwtToken)], data=ujson.dumps(payload)
        )
        resData = await res.json()

        assert res.status == 400
        assert resData["error"] == "New password does not meet length requirements"

    async def test_update_email_to_existing_account(
        self, test_server, create_account_jwt
    ):
        # guarantees there is already a "test@example.com" associated account.
        unusedJwt = await create_account_jwt

        payload = {"emailAddress": "guy_fieri@flavortown.com", "password": "123456"}
        res = await test_server.post("/signup", data=ujson.dumps(payload))
        resData = await res.json()

        jwtToken = resData["jwt"]
        updatePayload = {"emailAddress": "test@example.com"}
        updateRes = await test_server.put(
            "/account",
            headers=[("Authorization", jwtToken)],
            data=ujson.dumps(updatePayload),
        )
        updateResData = await updateRes.json()

        assert updateRes.status == 400
        assert updateResData["error"] == "Email address associated with another account"

    async def test_access_all_accounts(self, test_server, create_account_jwt):
        jwtToken = await create_account_jwt
        res = await test_server.get("/accounts", headers=[("Authorization", jwtToken)])

        assert res.status == 401

    async def test_access_specific_account(self, test_server, create_account_jwt):
        jwtToken = await create_account_jwt
        res = await test_server.get(
            "/accounts/1", headers=[("Authorization", jwtToken)]
        )

        assert res.status == 401

    async def test_delete_account(self, test_server, create_account_jwt):
        jwtToken = await create_account_jwt
        res = await test_server.delete(
            "/account", headers=[("Authorization", jwtToken)]
        )
        resData = await res.json()

        assert res.status == 200
        assert resData["success"] == "Account deleted"
