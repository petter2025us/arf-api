import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.base import Base
from app.database.session import SessionLocal
from app.api.deps import get_db
import os

# Use a real PostgreSQL URL from environment (will be set in CI)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://testuser:testpass@localhost:5432/testdb")

@pytest.fixture(scope="module")
def client():
    engine = create_engine(DATABASE_URL)
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
    app.dependency_overrides.clear()

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
    intent_id = eval_resp.json()["intent_id"]
    
    # 2. Record an outcome
    outcome_payload = {
        "intent_id": intent_id,
        "success": True,
        "recorded_by": "tester",
        "notes": "integration test"
    }
    outcome_resp = client.post("/api/v1/intents/outcome", json=outcome_payload, headers={"X-API-Key": "test-key"})
    assert outcome_resp.status_code == 200
