import ujson


class TestSignup:
    def test_valid_signup(self, test_server):
        payload = {"emailAddress": "test@example.com", "password": "123456"}
        res = test_server.post("/signup", data=ujson.dumps(payload))
        resData = res.json()

        assert res.status_code == 201
        assert "jwt" in resData
        assert resData["emailAddress"] == "test@example.com"
        assert resData["userRole"] == "USER"

    def test_short_pass(self, test_server, app_config):
        payload = {
            "emailAddress": "test@example.com",
            "password": "x" * (app_config.MIN_PASS_LENGTH - 1),
        }

        res = test_server.post("/signup", data=ujson.dumps(payload))

        assert res.status_code == 422

    def test_missing_password(self, test_server):
        payload = {"emailAddress": "test@example.com"}
        res = test_server.post("/signup", data=ujson.dumps(payload))

        assert res.status_code == 422

    def test_missing_email(self, test_server):
        payload = {"password": "asdfdfasdfas"}
        res = test_server.post("/signup", data=ujson.dumps(payload))

        assert res.status_code == 422

    def test_double_signup(self, test_server):
        payload = {"emailAddress": "test@example.com", "password": "123456"}
        res = test_server.post("/signup", data=ujson.dumps(payload))
        assert res.status_code == 201

        res2 = test_server.post("/signup", data=ujson.dumps(payload))

        assert res2.status_code == 409


class TestLogin:
    def test_login(self, test_server, create_account_jwt):
        # creates a "test@example.com" account
        unusedJwt = create_account_jwt  # NOQA

        payload = {"emailAddress": "test@example.com", "password": "123456"}

        res = test_server.post("/login", data=ujson.dumps(payload))
        resData = res.json()

        assert res.status_code == 200
        assert resData["emailAddress"] == "test@example.com"
        assert "jwt" in resData

    def test_invalid_password(self, test_server, create_account_jwt):
        # creates a "test@example.com" account
        unusedJwt = create_account_jwt  # NOQA

        payload = {"emailAddress": "test@example.com", "password": "incorrect_password"}

        res = test_server.post("/login", data=ujson.dumps(payload))

        assert res.status_code == 403

    def test_login_nonexistent_email(self, test_server):

        payload = {
            "emailAddress": "does_not_exist@example.com",
            "password": "some_password",
        }

        res = test_server.post("/login", data=ujson.dumps(payload))

        assert res.status_code == 404
