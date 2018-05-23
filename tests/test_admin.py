import pytest

import ujson


class TestAdminAccount:

    @pytest.fixture
    def admin_credentials(self, app_config):
        return {
            "emailAddress": app_config.ADMIN_EMAIL,
            "password": app_config.ADMIN_PASSWORD,
        }

    @pytest.fixture
    async def get_admin_jwt(self, test_server, admin_credentials):
        res = await test_server.post("/login", data=ujson.dumps(admin_credentials))
        resData = await res.json()
        return resData["jwt"]

    @pytest.fixture
    async def get_five_acccount_ids(self, test_server):
        accounts = []
        for i in range(1, 6):
            payload = {"emailAddress": f"test{i}@example.com", "password": "1234567"}
            res = await test_server.post("/signup", data=ujson.dumps(payload))
            resData = await res.json()
            accounts.append(resData["id"])
        return accounts

    async def test_unauthorized_access(self, test_server):
        res = await test_server.get("/accounts")
        assert res.status == 401

    async def test_get_info(self, test_server, get_admin_jwt, admin_credentials):
        jwtToken = await get_admin_jwt
        res = await test_server.get("/account", headers=[("Authorization", jwtToken)])
        resData = await res.json()

        assert res.status == 200
        assert "jwt" not in resData
        assert resData["emailAddress"] == admin_credentials["emailAddress"]
        assert resData["userRole"] == "ADMIN"

    async def test_update_role(self, test_server, get_admin_jwt):
        jwtToken = await get_admin_jwt
        payload = {"firstName": "thor", "lastName": "odinson", "userRole": "avenger"}
        res = await test_server.put(
            "/account", headers=[("Authorization", jwtToken)], data=ujson.dumps(payload)
        )
        resData = await res.json()

        assert res.status == 200
        assert resData["success"] == "Account updated"
        assert resData["firstName"] == "Thor"
        assert resData["lastName"] == "Odinson"
        assert resData["userRole"] == "AVENGER"

    async def test_access_all_accounts(
        self, test_server, get_admin_jwt, get_five_acccount_ids
    ):
        jwtToken = await get_admin_jwt
        userIds = await get_five_acccount_ids
        res = await test_server.get("/accounts", headers=[("Authorization", jwtToken)])
        resData = await res.json()

        assert res.status == 200
        assert "users" in resData
        assert len(userIds) == 5
        assert len(resData["users"]) == 6  # Including admin

    async def test_access_other_accounts(
        self, test_server, get_admin_jwt, get_five_acccount_ids
    ):
        jwtToken = await get_admin_jwt
        userIds = await get_five_acccount_ids

        for userId in userIds:
            res = await test_server.get(
                f"/accounts/{userId}", headers=[("Authorization", jwtToken)]
            )
            resData = await res.json()

            assert res.status == 200
            assert resData["id"] == userId

    async def test_update_other_accounts(
        self, test_server, get_admin_jwt, get_five_acccount_ids
    ):
        jwtToken = await get_admin_jwt
        userIds = await get_five_acccount_ids
        payload = {"firstName": "agent", "lastName": "smith"}

        for userId in userIds:
            res = await test_server.put(
                f"/accounts/{userId}",
                headers=[("Authorization", jwtToken)],
                data=ujson.dumps(payload),
            )
            resData = await res.json()

            assert res.status == 200
            assert resData["id"] == userId
            assert resData["firstName"] == "Agent"
            assert resData["lastName"] == "Smith"

    async def test_delete_other_accounts(
        self, test_server, get_admin_jwt, get_five_acccount_ids
    ):
        jwtToken = await get_admin_jwt
        userIds = await get_five_acccount_ids

        for userId in userIds:
            res = await test_server.delete(
                f"/accounts/{userId}", headers=[("Authorization", jwtToken)]
            )
            resData = await res.json()

            assert res.status == 200
            assert resData["success"] == "Account deleted"

    async def test_access_nonexistent_account(self, test_server, get_admin_jwt):
        jwtToken = await get_admin_jwt
        res = await test_server.get(
            "/accounts/10000", headers=[("Authorization", jwtToken)]
        )
        resData = await res.json()

        assert res.status == 404
        assert resData["error"] == "User not found"
