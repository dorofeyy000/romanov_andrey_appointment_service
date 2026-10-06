from fastapi.testclient import TestClient

from app.main import app

client=TestClient(app)

def test_appointments_require_authorization():
    response=client.get("/api/appointments")
    assert response.status_code==401

def test_login_rejects_invalid_password():
    response=client.post(
        "/api/auth/login",
        json={
            "username":"demo",
            "password":"wrong"
        }
    )

    assert response.status_code==401

def test_appointments_return_page_and_total():
    login=client.post(
        "/api/auth/login",
        json={
            "username":"demo",
            "password":"demo"
        }
    )

    assert login.status_code==200

    response=client.get(
        "/api/appointments?page=1&size=20"
    )

    assert response.status_code==200

    data=response.json()

    assert "items" in data
    assert "total" in data
    assert len(data["items"])<=20