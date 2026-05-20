from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint_returns_envelope() -> None:
    client = TestClient(create_app())

    response = client.get("/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["status"] == "ok"
    assert body["data"]["service"] == "GenAI Forge API"
    assert "request_id" in body["meta"]
    assert response.headers["x-request-id"].startswith("req_")