import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.base import Base
from app.api.deps import get_db

# Hardcode test database URL (matches docker-compose.test.yml)
TEST_DATABASE_URL = "postgresql://testuser:testpass@localhost:5432/testdb"

@pytest.fixture(scope="module")
def client():
    engine = create_engine(TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)

@pytest.mark.integration
def test_full_flow(client):
    # 1. Evaluate an intent
    eval_payload = {
        "intent_type": "provision_resource",
        "environment": "prod",
        "resource_type": "database",
        "region": "eastus",
        "size": "Standard",
        "estimated_cost": 1200,
        "policy_violations": [],
        "requester": "alice",
        "provenance": {},
        "configuration": {}
    }
    eval_resp = client.post("/api/v1/intents/evaluate", json=eval_payload, headers={"X-API-Key": "test-key"})
    assert eval_resp.status_code == 200
    data = eval_resp.json()
    intent_id = data.get("intent_id")
    assert intent_id is not None, "Response missing intent_id"

    # 2. Record an outcome
    outcome_payload = {
        "deterministic_id": intent_id,
        "success": True,
        "recorded_by": "tester",
        "notes": "Integration test outcome"
    }
    outcome_resp = client.post("/api/v1/intents/outcome", json=outcome_payload, headers={"X-API-Key": "test-key"})
    assert outcome_resp.status_code == 200
    outcome_data = outcome_resp.json()
    assert "outcome_id" in outcome_data

    # 3. Get risk (optional)
    risk_resp = client.get("/api/v1/get_risk", headers={"X-API-Key": "test-key"})
    assert risk_resp.status_code == 200
    risk_data = risk_resp.json()
    assert "system_risk" in risk_data
    assert risk_data["status"] in ["low", "moderate", "high", "critical"]
