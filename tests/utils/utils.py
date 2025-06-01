from typing import Dict
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.schemas.user import UserCreate
from app.crud import crud_user
from app.models.user import User

def create_random_user(db: Session) -> User:
    import random, string
    username = "".join(random.choices(string.ascii_lowercase, k=8))
    email = f"{username}@example.com"
    password = "password123"
    user_in = UserCreate(username=username, email=email, password=password)
    return crud_user.create_user(db, user_in=user_in)

def authentication_token_from_username(
    *, client: TestClient, username: str, password: str
) -> Dict[str, str]:
    data = {"username": username, "password": password}
    r = client.post(f"{settings.API_V1_STR}/auth/login/token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers