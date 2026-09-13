from fastapi.testclient import TestClient

from customer_intelligence.api.main import app


def test_health_endpoint_is_live() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}
