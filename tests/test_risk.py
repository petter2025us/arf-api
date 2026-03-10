import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_risk(client):
    response = client.get("/api/v1/get_risk", headers={"X-API-Key": "test-key"})
    assert response.status_code == 200
    data = response.json()
    assert "system_risk" in data
    assert data["status"] in ["low", "moderate", "high", "critical"]

def test_get_risk_internal_error(client, monkeypatch):
    # Force an exception in get_system_risk – patch the reference used in routes_risk
    def mock_get_system_risk():
        raise ValueError("test error")
    import app.api.routes_risk  # the module where get_system_risk is imported
    monkeypatch.setattr(app.api.routes_risk, "get_system_risk", mock_get_system_risk)
    response = client.get("/api/v1/get_risk", headers={"X-API-Key": "test-key"})
    assert response.status_code == 500
    assert response.json()["detail"] == "test error"
