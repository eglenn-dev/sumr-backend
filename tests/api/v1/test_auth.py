from fastapi.testclient import TestClient
from sqlmodel import Session
from app.core.config import settings
from app.models.user import User

def test_create_user(client: TestClient, db: Session):
    user_data = {"username": "newuser", "email": "newuser@example.com", "password": "newpassword123"}
    response = client.post(f"{settings.API_V1_STR}/auth/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data

    response_dup_username = client.post(f"{settings.API_V1_STR}/auth/users/", json=user_data)
    assert response_dup_username.status_code == 400

    user_data_dup_email = {"username": "anotheruser", "email": "newuser@example.com", "password": "newpassword123"}
    response_dup_email = client.post(f"{settings.API_V1_STR}/auth/users/", json=user_data_dup_email)
    assert response_dup_email.status_code == 400


def test_login_for_access_token(client: TestClient, test_user_data: dict, test_user: User):
    login_data = {"username": test_user_data["username"], "password": test_user_data["password"]}
    response = client.post(f"{settings.API_V1_STR}/auth/login/token", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"

    wrong_login_data = {"username": test_user_data["username"], "password": "wrongpassword"}
    response_wrong = client.post(f"{settings.API_V1_STR}/auth/login/token", data=wrong_login_data)
    assert response_wrong.status_code == 401


def test_read_current_user(client: TestClient, auth_token_headers: dict, test_user_data: dict):
    response = client.get(f"{settings.API_V1_STR}/auth/users/me", headers=auth_token_headers)
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == test_user_data["username"]
    assert user["email"] == test_user_data["email"]
    assert "hashed_password" not in user