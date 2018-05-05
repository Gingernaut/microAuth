import sys
import pytest
sys.path.append("./app")

from config import get_config
from create_app import create_app
from db.db_client import db
from models.base import Base
from utils.init_db import init_db


@pytest.fixture
def app_config():
    return get_config("TESTING")


@pytest.yield_fixture
def app():
    """
    Run for each test. init_db environment specified to prevent tests being run against
    Production database even if API_ENV in .env is set to PRODUCTION.
    """
    init_db("TESTING")
    yield create_app("TESTING")


@pytest.fixture
def test_server(loop, app, test_client):
    return loop.run_until_complete(test_client(app))


# initialize database when tests are done.
def pytest_sessionfinish(session):
    init_db("TESTING")
