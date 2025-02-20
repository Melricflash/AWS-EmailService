import json

import pytest
from app import app

@pytest.fixture
def client():
    # Configure Flask app for testing
    app.config['TESTING'] = True
    app.config['DEBUG'] = False

    # Create a test client
    with app.test_client() as client:
        yield client

def test_get_health(client):
    response = client.get("/")
    assert response.status_code == 200