# API Endpoints

This page lists all available API endpoints.

General

- All API routers are mounted under the `/api/v1` prefix (see `app.main`).
- Health endpoint is available at `/health`.

Health

- GET /health
  - Returns: `{ "status": "ok" }`
  - Purpose: basic liveness/health check.

Governance (risk/intent evaluation)

- POST /api/v1/intents/evaluate
  - Description: Evaluate an infrastructure intent and return a risk score and explanation.
  - Body: an InfrastructureIntentRequest JSON object (see the model in `app.models.infrastructure_intents`).
  - Behaviour: The endpoint converts the incoming intent to an OSS intent and calls into the locally initialized RiskEngine (`app.state.risk_engine`).
  - Errors: May return 500 if evaluation fails.

- POST /api/v1/intents/outcome
  - Description: Record the observed outcome of an executed intent to update priors.
  - Behaviour: Not implemented in this repository; the endpoint returns a `501 Not Implemented` (the current implementation raises a 501 indicating outcome recording is not yet implemented).

Other routers

- The application also registers routers for incidents, risk, intents, and history at `/api/v1` (see `app.main`). Consult the respective modules in `app.api` for their exact endpoints and payloads.

Notes

- The governance evaluation relies on a `RiskEngine` instance initialized at app startup (see `app.main`) which reads `ARF_HMC_MODEL` and `ARF_USE_HYPERPRIORS` environment variables.
