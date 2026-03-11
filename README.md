# arf-api

ARF API Control Plane (FastAPI)

Quick start

1. Install dependencies:

   pip install -r requirements.txt

   Note: `requirements.txt` installs `agentic-reliability-framework` directly from the project's Git repository.

2. Set any needed environment variables in a `.env` file (the app uses pydantic-settings and will read `.env`):

   - ARF_HMC_MODEL (path to HMC model JSON; default: `models/hmc_model.json`)
   - ARF_USE_HYPERPRIORS (true/false)
   - API_KEY (optional — currently not enforced by routes)

3. Run the app locally:

   uvicorn app.main:app --reload --port 8000

4. Health check:

   GET http://localhost:8000/health

Tests

- Run `pytest`. Tests use a temporary SQLite DB (`sqlite:///./test.db`) created by the test fixtures.

Notes

- The governance endpoints use an in-process RiskEngine initialized at startup. The outcome recording endpoint is not implemented in this repository and returns HTTP 501.
