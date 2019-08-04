# flake8: noqa: E402
import sys
import pytest
import ujson

sys.path.append("./app")
from config import get_config
from create_app import create_app
from db.db_client import db
from utils.init_db import init_db

from starlette.testclient import TestClient


@pytest.fixture
def app_config():
    return get_config("TESTING")


@pytest.fixture
def init_app(app_config):
    # Re-initializes local postgres DB before each test
    init_db(app_config.API_ENV)
    yield create_app(app_config)


@pytest.fixture
def test_server(init_app):
    return TestClient(init_app)


@pytest.fixture
def db_session():
    session = db.new_session()
    yield session
    session.remove()


@pytest.fixture
def create_account_jwt(test_server):
    payload = {"emailAddress": "test@example.com", "password": "123456"}
    res = test_server.post("/signup", data=ujson.dumps(payload))
    resData = res.json()
    return resData["jwt"]


# initialize database when tests are done.
def pytest_sessionfinish(session):
    init_db("TESTING")
