import pytest
import json
import os

@pytest.fixture
def client(load_app):
    with load_app.test_client() as client:
        yield client

# Test for reaching the health check successfully
def test_get_homepage(client):
    response = client.get("/")
    assert response.status_code == 200