import pytest
from fastapi.testclient import TestClient

from app.main import app, repo


@pytest.fixture(autouse=True)
def _reset_storage():
    repo._reset()
    yield
    repo._reset()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def created_task(client: TestClient) -> dict:
    response = client.post("/tasks", json={"title": "fixture task"})
    assert response.status_code == 201
    return response.json()
