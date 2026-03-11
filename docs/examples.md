# Examples

This page provides usage examples for the ARF API.

Check health

curl example:

curl http://localhost:8000/health

Response:

{
  "status": "ok"
}

Evaluate an intent (governance)

- Endpoint: POST /api/v1/intents/evaluate
- Content-Type: application/json

Example payload (minimal illustrative example — adapt to the `InfrastructureIntentRequest` model used by the project):

{
  "id": "intent-123",
  "description": "Example infrastructure change",
  "estimated_cost": 100.0,
  "policy_violations": []
}

Curl example:

curl -X POST http://localhost:8000/api/v1/intents/evaluate \
  -H "Content-Type: application/json" \
  -d '{"id":"intent-123","description":"Example","estimated_cost":100.0,"policy_violations":[]} '

Python (requests) example:

import requests

payload = {
    "id": "intent-123",
    "description": "Example infrastructure change",
    "estimated_cost": 100.0,
    "policy_violations": []
}

resp = requests.post("http://localhost:8000/api/v1/intents/evaluate", json=payload)
print(resp.status_code, resp.text)

Notes

- The evaluate endpoint uses an in-process `RiskEngine` (initialized in `app.main`) to compute risk and explanations.
- The `/api/v1/intents/outcome` endpoint exists but currently returns 501 Not Implemented — outcome recording/storage is incomplete in this repo.
