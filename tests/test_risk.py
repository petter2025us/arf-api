from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_risk():
    response = client.get("/api/v1/get_risk")
    assert response.status_code == 200
    data = response.json()
    assert "system_risk" in data
    assert "status" in data

def test_get_risk_internal_error(client, monkeypatch):
    # Force an exception in get_system_risk
    def mock_get_system_risk():
        raise ValueError("test error")
    import app.services.risk_service
    monkeypatch.setattr(app.services.risk_service, "get_system_risk", mock_get_system_risk)
    response = client.get("/api/v1/get_risk", headers={"X-API-Key": "test-key"})
    assert response.status_code == 500
