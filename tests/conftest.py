import pytest
from app import create_app
from config.config import config

@pytest.fixture(scope='session')
def app():
    app = create_app(config['testing'])
    return app

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

@pytest.fixture(scope='session')
def runner(app):
    return app.test_cli_runner()