
import sys
import pytest
sys.path.append('./app')

from create_app import create_app
from db.db_client import db
from utils.init_db import init_db
from models.base import Base

@pytest.yield_fixture
def app():
    db.init_engine()
    Base.metadata.drop_all(bind=db.engine)
    db.create_tables()
    yield create_app("TESTING")


@pytest.fixture
def test_server(loop, app, test_client):
    return loop.run_until_complete(test_client(app))
