import pytest
from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_evaluate_provision_intent():
    payload = {
        "intent_type": "ProvisionResourceIntent",
        "environment": "prod",
        "resource_type": "DATABASE",
        "region": "eastus",
        "size": "Standard",
        "estimated_cost": 1200,
        "policy_violations": [],
        "requester": "alice",
        "provenance": {}
    }
    response = client.post("/api/v1/intents/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "explanation" in data
    assert "contributions" in data

def test_evaluate_grant_access():
    payload = {
        "intent_type": "GrantAccessIntent",
        "environment": "dev",
        "principal": "bob",
        "permission_level": "READ",
        "resource_scope": "/subscriptions/123",
        "estimated_cost": None,
        "policy_violations": [],
        "requester": "alice",
        "provenance": {}
    }
    response = client.post("/api/v1/intents/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data

def test_evaluate_deploy_config():
    payload = {
        "intent_type": "DeployConfigurationIntent",
        "environment": "staging",
        "service_name": "payments-api",
        "change_scope": "canary",
        "deployment_target": "staging",
        "estimated_cost": 20,
        "policy_violations": [],
        "requester": "alice",
        "provenance": {}
    }
    response = client.post("/api/v1/intents/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data

def test_invalid_intent_type():
    payload = {
        "intent_type": "UnknownIntent",
        "environment": "prod",
        "requester": "alice"
    }
    response = client.post("/api/v1/intents/evaluate", json=payload)
    assert response.status_code == 422  # Unprocessable Entity (validation error)
