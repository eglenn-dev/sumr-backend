import pytest
from typing import Generator, Any
from fastapi.testclient import TestClient
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool
from app.main import app
from app.api.deps import get_current_active_user, get_current_user
from app.db.session import get_db
from app.core.config import settings
from app.models.user import User
from app.core.security import create_access_token
from app.schemas.user import UserCreate
from app.crud.crud_user import create_user as crud_create_user 

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

def override_get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

@pytest.fixture(scope="function", autouse=True)
def db_setup_session():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db(db_setup_session) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(db_setup_session) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user_data() -> dict:
    return {"username": "testuser", "email": "test@example.com", "password": "testpassword"}

@pytest.fixture(scope="function")
def test_user(db: Session, test_user_data: dict) -> User:
    user = db.exec(select(User).where(User.username == test_user_data["username"])).first()
    if not user:
        user_in = UserCreate(
            username=test_user_data["username"],
            email=test_user_data["email"],
            password=test_user_data["password"]
        )
        user = crud_create_user(db=db, user_in=user_in)
    return user

@pytest.fixture(scope="function")
def auth_token_headers(test_user: User) -> dict[str, str]:
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}

def override_get_current_active_user_for_test_user(db: Session = Depends(override_get_db)):
    user = db.exec(select(User).where(User.username == "testuser")).first()
    if not user:
        user_in = UserCreate(username="testuser", email="test@example.com", password="testpassword")
        user = crud_create_user(db=db, user_in=user_in)
    return user