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
    def get_admin_jwt(self, test_server, admin_credentials):
        res = test_server.post("/login", data=ujson.dumps(admin_credentials))
        resData = res.json()
        return resData["jwt"]

    @pytest.fixture
    def get_five_acccount_ids(self, test_server):
        accounts = []
        for i in range(1, 6):
            payload = {"emailAddress": f"test{i}@example.com", "password": "1234567"}
            res = test_server.post("/signup", data=ujson.dumps(payload))
            resData = res.json()
            accounts.append(resData["id"])
        return accounts

    def test_unauthorized_users_access(self, test_server):
        response = test_server.get("/accounts")
        assert response.status_code == 401

    def test_get_info(self, test_server, get_admin_jwt, admin_credentials):
        res = test_server.get(
            "/account", headers={"Authorization": f"Bearer {get_admin_jwt}"}
        )
        resData = res.json()

        assert res.status_code == 200
        assert "jwt" not in resData
        assert resData["emailAddress"] == admin_credentials["emailAddress"]
        assert resData["userRole"] == "ADMIN"

    def test_update_role(self, test_server, get_admin_jwt):
        payload = {"firstName": "Thor", "lastName": "Odinson", "userRole": "AVENGER"}
        res = test_server.put(
            "/account",
            headers={"Authorization": f"Bearer {get_admin_jwt}"},
            data=ujson.dumps(payload),
        )
        resData = res.json()

        # assert res.status_code == 200
        assert resData["firstName"] == "Thor"
        assert resData["lastName"] == "Odinson"
        assert resData["userRole"] == "AVENGER"

    def test_access_all_accounts(
        self, test_server, get_admin_jwt, get_five_acccount_ids
    ):
        res = test_server.get(
            "/accounts", headers={"Authorization": f"Bearer {get_admin_jwt}"}
        )
        resData = res.json()

        assert res.status_code == 200
        assert len(resData) == 6  # Including admin

    def test_access_other_accounts(
        self, test_server, get_admin_jwt, get_five_acccount_ids
    ):
        admin_jwt = get_admin_jwt
        for userId in get_five_acccount_ids:
            res = test_server.get(
                f"/accounts/{userId}", headers={"Authorization": f"Bearer {admin_jwt}"}
            )
            resData = res.json()

            assert res.status_code == 200
            assert resData["id"] == userId

    def test_update_other_accounts(
        self, test_server, get_admin_jwt, get_five_acccount_ids
    ):
        payload = {"firstName": "agent", "lastName": "smith"}
        admin_jwt = get_admin_jwt
        for userId in get_five_acccount_ids:
            res = test_server.put(
                f"/accounts/{userId}",
                headers={"Authorization": f"Bearer {admin_jwt}"},
                data=ujson.dumps(payload),
            )
            resData = res.json()

            assert res.status_code == 200
            assert resData["id"] == userId
            assert resData["firstName"] == "agent"
            assert resData["lastName"] == "smith"

    # TODO: Add test case for successful and non-successful email update

    def test_delete_other_accounts(
        self, test_server, get_admin_jwt, get_five_acccount_ids
    ):
        admin_jwt = get_admin_jwt
        for userId in get_five_acccount_ids:
            res = test_server.delete(
                f"/accounts/{userId}", headers={"Authorization": f"Bearer {admin_jwt}"}
            )
            assert res.status_code == 200

    def test_access_nonexistent_account(self, test_server, get_admin_jwt):
        res = test_server.get(
            f"/accounts/10000", headers={"Authorization": f"Bearer {get_admin_jwt}"}
        )
        assert res.status_code == 404
