import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DB_URL = "sqlite:///./test_users.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def test_register_user(client):
    resp = client.post("/users/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "alice"
    assert "password" not in data  # password must not appear in response


def test_register_duplicate_username(client):
    client.post("/users/register", json={
        "username": "bob",
        "email": "bob@example.com",
        "password": "secret"
    })
    resp = client.post("/users/register", json={
        "username": "bob",
        "email": "bob2@example.com",
        "password": "secret"
    })
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/users/register", json={
        "username": "charlie",
        "email": "charlie@example.com",
        "password": "mypassword"
    })
    resp = client.post("/users/login", json={
        "username": "charlie",
        "password": "mypassword"
    })
    assert resp.status_code == 200
    assert "token" in resp.json()


def test_login_wrong_password(client):
    client.post("/users/register", json={
        "username": "dave",
        "email": "dave@example.com",
        "password": "correctpass"
    })
    resp = client.post("/users/login", json={
        "username": "dave",
        "password": "wrongpass"
    })
    assert resp.status_code == 401
