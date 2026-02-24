import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User

TEST_DB_URL = "sqlite:///./test_taskmanager.db"
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


@pytest.fixture
def auth_headers(client):
    client.post("/users/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    resp = client.post("/users/login", json={
        "username": "testuser",
        "password": "password123"
    })
    token = resp.json()["token"]
    return {"x-token": token}


def test_create_task(client, auth_headers):
    resp = client.post("/tasks/", json={
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "priority": "high"
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Buy groceries"
    assert data["status"] == "todo"
    assert data["priority"] == "high"


def test_list_tasks(client, auth_headers):
    client.post("/tasks/", json={"title": "Task 1"}, headers=auth_headers)
    client.post("/tasks/", json={"title": "Task 2"}, headers=auth_headers)
    resp = client.get("/tasks/", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_update_task_status(client, auth_headers):
    create_resp = client.post("/tasks/", json={"title": "Finish report"}, headers=auth_headers)
    task_id = create_resp.json()["id"]
    resp = client.put(f"/tasks/{task_id}", json={"status": "in_progress"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


@pytest.mark.skip(reason="TODO: implement — 404 handling not yet in place")
def test_get_nonexistent_task_returns_404(client, auth_headers):
    resp = client.get("/tasks/99999", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.skip(reason="TODO: implement — pagination not yet supported")
def test_list_tasks_pagination(client, auth_headers):
    for i in range(25):
        client.post("/tasks/", json={"title": f"Task {i}"}, headers=auth_headers)
    resp = client.get("/tasks/?page=1&limit=10", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 10
