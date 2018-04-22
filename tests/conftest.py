
import sys
import pytest

from config import get_config
from create_app import create_app
from init_db import db

sys.path.append('./app')

@pytest.yield_fixture
def app():
    db.init_engine()
    db.connect()
    yield create_app("TESTING")
    db.close()


@pytest.fixture
def config():
    return get_config()

@pytest.fixture
def test_server(loop, app, test_client):
    return loop.run_until_complete(test_client(app))
