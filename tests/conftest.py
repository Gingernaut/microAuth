import sys
import pytest
sys.path.append('./app')

from create_app import create_app
from db.db_client import db
from utils.init_db import init_db
from models.base import Base
from config import get_config

@pytest.yield_fixture
def app():
    # reinitialize database and creates admin. Run for each test.
    db.init_engine()
    Base.metadata.drop_all(bind=db.engine)
    db.create_tables()
    yield create_app("TESTING")


@pytest.fixture
def test_server(loop, app, test_client):
    return loop.run_until_complete(test_client(app))

@pytest.fixture
def app_config():
    return get_config("TESTING")
