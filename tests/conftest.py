
import sys
import pytest
sys.path.append('./app')

from create_app import create_app


@pytest.yield_fixture
def app():
    yield create_app("TESTING")


@pytest.fixture
def test_server(loop, app, test_client):
    return loop.run_until_complete(test_client(app))
