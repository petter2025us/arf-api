from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_simulate_intent():
    payload = {"action": "restart_service", "target": "api-gateway"}
    response = client.post("/api/v1/simulate_intent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert data["recommendation"] in ["safe_to_execute", "requires_approval", "blocked"]
import logging

def test_simulate_intent_deprecation_warning(caplog):
    from app.services.intent_service import simulate_intent
    from app.models.intent_models import IntentSimulation
    intent = IntentSimulation(action="restart_service", target="test")
    with caplog.at_level(logging.WARNING):
        result = simulate_intent(intent)
    assert "Deprecated endpoint" in caplog.text
    assert "risk_score" in result
    assert result["recommendation"] in ["safe_to_execute", "requires_approval", "blocked"]
