import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_contact():
    response = client.post("/contacts/", json={"name": "John Doe", "email": "john@example.com"})
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"


def test_read_contacts():
    response = client.get("/contacts/")
    assert response.status_code == 200


def test_delete_contact():
    create_response = client.post("/contacts/", json={"name": "Jane Doe", "email": "jane@example.com"})

    contact_id = create_response.json()["id"]

    delete_response = client.delete(f"/contacts/{contact_id}")

    assert delete_response.status_code == 200


def test_read_nonexistent_contact():
    response = client.get("/contacts/9999")
    assert response.status_code == 404
