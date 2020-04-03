# flake8: noqa: E402
import sys
import pytest
import ujson
from starlette.testclient import TestClient
from testcontainers.postgres import PostgresContainer

sys.path.append("./app")
from config import get_config
from create_app import create_app
from db.db_client import db
from utils.init_db import init_db

config = get_config("TESTING")


class TestContainer(PostgresContainer):
    POSTGRES_USER = config.DB_USERNAME
    POSTGRES_PASSWORD = config.DB_PASSWORD
    POSTGRES_DB = config.DB_NAME


container = TestContainer("postgres:11.4")


@pytest.fixture
def app_config():
    return config


@pytest.fixture(autouse=True)
def get_db_container(monkeypatch):
    monkeypatch.setattr(db, "get_conn_str", container.get_connection_url)
    yield container


@pytest.fixture
def init_app(app_config, get_db_container):
    with get_db_container as postgres:
        init_db(app_config.API_ENV)
        yield create_app(app_config)


@pytest.fixture
def test_server(init_app):
    return TestClient(init_app)


@pytest.fixture
def db_session(app_config):
    db.initialize_connection(app_config.API_ENV)
    session = db.new_session()
    yield session
    session.remove()


@pytest.fixture
def create_account_jwt(test_server):
    payload = {"emailAddress": "test@example.com", "password": "123456"}
    res = test_server.post("/signup", data=ujson.dumps(payload))
    resData = res.json()
    return resData["jwt"]
