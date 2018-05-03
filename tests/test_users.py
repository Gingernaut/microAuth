import ujson
import pytest


class TestSignup:

    async def test_valid_signup(self, test_server):
        payload = {
            "emailAddress": "test@example.com",
            "password": "123456"
        }
        res = await test_server.post("/signup", data=ujson.dumps(payload))
        res_data = await res.json()

        assert res.status == 201
        assert "jwt" in res_data
        assert res_data["emailAddress"] == "test@example.com"
        assert res_data["userRole"] == "USER"

    async def test_short_pass(self, test_server):
        payload = {
            "emailAddress": "test@example.com",
            "password": "12345"
        }

        res = await test_server.post("/signup", data=ujson.dumps(payload))
        res_data = await res.json()

        assert res.status == 400
        assert res_data["error"] == "Password does not meet required length requirements"

    async def test_missing_pass(self, test_server):
        payload = {"emailAddress": "test@example.com"}
        res = await test_server.post("/signup", data=ujson.dumps(payload))
        res_data = await res.json()

        assert res.status == 400
        assert res_data["error"] == "No password provided"

    async def test_missing_email(self, test_server):
        payload = {"password": "asdfdfasdfas"}
        res = await test_server.post("/signup", data=ujson.dumps(payload))
        res_data = await res.json()

        assert res.status == 400
        assert res_data["error"] == "No email address provided"

    async def test_double_signup(self, test_server):
        payload = {
            "emailAddress": "test@example.com",
            "password": "123456"
        }
        res = await test_server.post("/signup", data=ujson.dumps(payload))
        assert res.status == 201

        res2 = await test_server.post("/signup", data=ujson.dumps(payload))
        res2_data = await res2.json()

        assert res2.status == 400
        assert res2_data["error"] == "An account with that email address already exists"


class TestAccount:

    @pytest.fixture
    async def create_account_jwt(self, test_server):
        payload = {
            "emailAddress": "test@example.com",
            "password": "123456"
        }
        res = await test_server.post("/signup", data=ujson.dumps(payload))
        res_data = await res.json()
        return res_data["jwt"]

    async def test_get_account_without_auth(self, test_server):
        res = await test_server.get("/account")
        assert res.status == 401

    async def test_get_info(self, test_server, create_account_jwt):
        jwt_token = await create_account_jwt
        res = await test_server.get("/account", headers=[("Authorization", jwt_token)])
        res_data = await res.json()

        assert res.status == 200
        assert "jwt" not in res_data
        assert res_data["emailAddress"] == "test@example.com"
        assert res_data["userRole"] == "USER"
        assert res_data["firstName"] == None
        assert res_data["isValidated"] == False

    async def test_valid_update(self, test_server, create_account_jwt):
        jwt_token = await create_account_jwt
        payload = {
            "firstName": "jason",
            "lastName": "bourne",
            "emailAddress": ""
        }
        res = await test_server.put("/account", headers=[("Authorization", jwt_token)], data=ujson.dumps(payload))
        res_data = await res.json()

        assert res.status == 200
        assert res_data["success"] == "Account updated"
        assert res_data["firstName"] == "Jason"
        assert res_data["lastName"] == "Bourne"

    async def test_update_own_role(self, test_server, create_account_jwt):
        jwt_token = await create_account_jwt
        payload = { "userRole": "ADMIN"}
        res = await test_server.put("/account", headers=[("Authorization", jwt_token)], data=ujson.dumps(payload))
        res_data = await res.json()

        assert res.status == 401
        assert res_data["error"] == "Cannot update role"

    async def test_update_password(self, test_server, create_account_jwt):
        jwt_token = await create_account_jwt
        payload = {"password": "super_much_secure"}
        res = await test_server.put("/account", headers=[("Authorization", jwt_token)], data=ujson.dumps(payload))
        res_data = await res.json()

        assert res.status == 200
        assert res_data["success"] == "Account updated"

        login_data = {
            "emailAddress": res_data["emailAddress"],
            "password": "super_much_secure"
        }

        login_res = await test_server.post("/login", data=ujson.dumps(login_data))
        login_res_data = await login_res.json()

        assert login_res.status == 200
        assert login_res_data["emailAddress"] == res_data["emailAddress"]

    async def test_update_email_to_existing_account(self, test_server, create_account_jwt):
        # guarantees there is already a "test@example.com" associated account.
        unused_jwt = await create_account_jwt

        payload = {
            "emailAddress": "guy_fieri@flavortown.com",
            "password": "123456"
        }
        res = await test_server.post("/signup", data=ujson.dumps(payload))
        res_data = await res.json()

        jwt_token = res_data["jwt"]
        update_payload = {"emailAddress": "test@example.com"}
        update_res = await test_server.put("/account", headers=[("Authorization", jwt_token)], data=ujson.dumps(update_payload))
        update_res_data = await update_res.json()

        assert update_res.status == 400
        assert update_res_data["error"] == "Email address associated with another account"

    async def test_short_pass_update(self, test_server, create_account_jwt):
        jwt_token = await create_account_jwt
        payload = {
            "password": "1234"
        }
        res = await test_server.put("/account", headers=[("Authorization", jwt_token)], data=ujson.dumps(payload))
        res_data = await res.json()

        assert res.status == 400
        assert res_data["error"] == "New password does not meet length requirements"

    async def test_access_all_accounts(self, test_server, create_account_jwt):
        jwt_token = await create_account_jwt
        res = await test_server.get("/accounts", headers=[("Authorization", jwt_token)])

        assert res.status == 401

    async def test_access_specific_account(self, test_server, create_account_jwt):
        jwt_token = await create_account_jwt
        res = await test_server.get("/accounts/1", headers=[("Authorization", jwt_token)])

        assert res.status == 401

    async def test_delete_account(self, test_server, create_account_jwt):
        jwt_token = await create_account_jwt
        res = await test_server.delete("/account", headers=[("Authorization", jwt_token)])
        res_data = await res.json()

        assert res.status == 200
        assert res_data["success"] == "Account deleted"
