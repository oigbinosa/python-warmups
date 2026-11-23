import copy

import pytest
from fastapi.testclient import TestClient

from ex4_api import app, requests_db

client = TestClient(app)

# A valid request to reuse across tests
VALID_REQUEST = {
    "id": "PR-1001",
    "vendor": "Northeast Safety Supply",
    "lineItems": [
        {"description": "Insulated work gloves", "quantity": 10, "unit_price": 12.50},
        {"description": "Hard hat, Class E", "quantity": 4, "unit_price": 37.25},
    ],
    "total": 274.00,
}


@pytest.fixture(autouse=True)
def clear_db():
    """Runs before every test"""
    requests_db.clear()
    yield


def test_create_request_returns_201():
    response = client.post("/requests", json=VALID_REQUEST)

    assert response.status_code == 201
    assert response.json()["id"] == "PR-1001"


def test_duplicate_request_returns_409():
    client.post("/requests", json=VALID_REQUEST)
    response = client.post("/requests", json=VALID_REQUEST)

    assert response.status_code == 409


def test_get_existing_request_returns_200():
    client.post("/requests", json=VALID_REQUEST)
    response = client.get("/requests/PR-1001")

    assert response.status_code == 200


def test_get_missing_request_returns_404():
    response = client.get("/requests/PR-9999")

    assert response.status_code == 404


def test_negative_quantity_returns_422():
    deep = copy.deepcopy(VALID_REQUEST)
    deep["lineItems"][0]["quantity"] = 8

    response = client.post("/requests", json=deep)

    assert response.status_code == 422


def test_wrong_total_returns_422():
    deep = copy.deepcopy(VALID_REQUEST)
    deep["total"] = 273

    response = client.post("/requests", json=deep)

    assert response.status_code == 422
    assert "quantity" in response.text
