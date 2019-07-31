import ujson


class TestAccount:
    def test_get_account_without_auth(self, test_server):
        res = test_server.get("/account")
        assert res.status_code == 401

    def test_get_info(self, test_server, create_account_jwt):
        res = test_server.get(
            "/account", headers={"Authorization": f"Bearer {create_account_jwt}"}
        )
        resData = res.json()

        assert res.status_code == 200
        assert "jwt" not in resData
        assert resData["emailAddress"] == "test@example.com"
        assert resData["userRole"] == "USER"
        assert resData["isVerified"] is False

    def test_valid_update(self, test_server, create_account_jwt):
        payload = {"firstName": "Jason", "lastName": "Bourne", "emailAddress": ""}
        res = test_server.put(
            "/account",
            headers={"Authorization": f"Bearer {create_account_jwt}"},
            data=ujson.dumps(payload),
        )
        resData = res.json()

        assert res.status_code == 200
        assert resData["firstName"] == "Jason"
        assert resData["lastName"] == "Bourne"
        assert resData["createdTime"] < resData["modifiedTime"]
        assert resData["emailAddress"] == "test@example.com"

    def test_update_own_role(self, test_server, create_account_jwt):
        payload = {"userRole": "ADMIN"}
        res = test_server.put(
            "/account",
            headers={"Authorization": f"Bearer {create_account_jwt}"},
            data=ujson.dumps(payload),
        )

        assert res.status_code == 403

    def test_update_password(self, test_server, create_account_jwt):
        payload = {"password": "super_much_secure"}
        res = test_server.put(
            "/account",
            headers={"Authorization": f"Bearer {create_account_jwt}"},
            data=ujson.dumps(payload),
        )
        assert res.status_code == 200
        resData = res.json()

        login_data = {
            "emailAddress": resData["emailAddress"],
            "password": "super_much_secure",
        }

        login_res = test_server.post("/login", data=ujson.dumps(login_data))
        login_resData = login_res.json()

        assert login_res.status_code == 200
        assert login_resData["emailAddress"] == resData["emailAddress"]

    def test_short_pass_update(self, test_server, create_account_jwt, app_config):
        payload = {"password": "x" * (app_config.MIN_PASS_LENGTH - 1)}
        res = test_server.put(
            "/account",
            headers={"Authorization": f"Bearer {create_account_jwt}"},
            data=ujson.dumps(payload),
        )

        assert res.status_code == 422

    def test_update_email_to_existing_account(self, test_server, create_account_jwt):
        # guarantees there is already a "test@example.com" associated account.
        unusedJwt = create_account_jwt  # NOQA

        payload = {"emailAddress": "guy_fieri@flavortown.com", "password": "123456"}
        res = test_server.post("/signup", data=ujson.dumps(payload))
        resData = res.json()

        jwtToken = resData["jwt"]
        updatePayload = {"emailAddress": "test@example.com"}
        updateRes = test_server.put(
            "/account",
            headers={"Authorization": f"Bearer {jwtToken}"},
            data=ujson.dumps(updatePayload),
        )

        assert updateRes.status_code == 403

    def test_update_email_to_own_email(self, test_server, create_account_jwt):
        # guarantees there is already a "test@example.com" associated account.
        unusedJwt = create_account_jwt  # NOQA

        payload = {"emailAddress": "guy_fieri@flavortown.com", "password": "123456"}
        res = test_server.post("/signup", data=ujson.dumps(payload))
        resData = res.json()

        jwtToken = resData["jwt"]
        updatePayload = {
            "emailAddress": "guy_fieri@flavortown.com",
            "firstName": "flavor-dealer",
        }
        updateRes = test_server.put(
            "/account",
            headers={"Authorization": f"Bearer {jwtToken}"},
            data=ujson.dumps(updatePayload),
        )

        assert updateRes.status_code == 200
        assert updateRes.json()["firstName"] == "flavor-dealer"

    def test_access_all_users(self, test_server, create_account_jwt):
        res = test_server.get(
            "/accounts", headers={"Authorization": f"Bearer {create_account_jwt}"}
        )

        assert res.status_code == 403

    def test_access_specific_user(self, test_server, create_account_jwt):
        res = test_server.get(
            "/accounts/1", headers={"Authorization": f"Bearer {create_account_jwt}"}
        )

        assert res.status_code == 403

    def test_delete_account(self, test_server, create_account_jwt):
        res = test_server.delete(
            "/account", headers={"Authorization": f"Bearer {create_account_jwt}"}
        )

        assert res.status_code == 200

        deleted_credentials = {"emailAddress": "test@example.com", "password": "123456"}
        res2 = test_server.post("/login", data=ujson.dumps(deleted_credentials))

        assert res2.status_code == 404
