from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_invalid_state_filter_is_400() -> None:
    r = client.get("/api/tasks", params={"state": "FOO"})
    assert r.status_code == 400
