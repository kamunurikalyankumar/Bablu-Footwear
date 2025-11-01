import pytest
from app import create_app
from config.config import config

@pytest.fixture
def app():
    app = create_app(config['testing'])
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_shop_page(client):
    response = client.get('/shop')
    assert response.status_code == 200

def test_contact_page(client):
    response = client.get('/contact')
    assert response.status_code == 200