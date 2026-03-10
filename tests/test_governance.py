import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_evaluate_provision_intent(client):
    payload = {
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
    response = client.post("/api/v1/intents/evaluate", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "risk_score" in data

def test_evaluate_grant_access(client):
    payload = {
        "intent_type": "grant_access",
        "environment": "dev",
        "principal": "bob",
        "permission_level": "read",
        "resource_scope": "/subscriptions/123",
        "estimated_cost": None,
        "policy_violations": [],
        "requester": "alice",
        "provenance": {},
        "justification": "test"
    }
    response = client.post("/api/v1/intents/evaluate", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "risk_score" in data

def test_evaluate_deploy_config(client):
    payload = {
        "intent_type": "deploy_config",
        "environment": "staging",
        "service_name": "payments-api",
        "change_scope": "canary",
        "deployment_target": "staging",
        "estimated_cost": 20,
        "policy_violations": [],
        "requester": "alice",
        "provenance": {},
        "configuration": {}
    }
    response = client.post("/api/v1/intents/evaluate", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "risk_score" in data

def test_invalid_intent_type(client):
    payload = {
        "intent_type": "UnknownIntent",
        "environment": "prod",
        "requester": "alice",
        "provenance": {}
    }
    response = client.post("/api/v1/intents/evaluate", json=payload)
    assert response.status_code == 422
