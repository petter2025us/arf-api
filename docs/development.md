# Development

This page explains how to set up the ARF API for local development.

Requirements

- Python 3.10+ (match your environment)
- A virtual environment
- The project's Python dependencies (see `requirements.txt`). Note: `agentic-reliability-framework` is installed from a Git URL in `requirements.txt`.

Quick start

1. Clone the repository:

   git clone https://github.com/petter2025us/arf-api.git
   cd arf-api

2. Create and activate a virtualenv, then install dependencies:

   python -m venv .venv
   source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
   pip install -r requirements.txt

3. Configure environment variables (optional):

   - The project uses pydantic-settings with `env_file = ".env"` (see `app/core/config.py`). Create a `.env` file to set values locally.

   Relevant environment variables used by the code:
   - ARF_HMC_MODEL (default: `models/hmc_model.json`) — path to HMC model JSON used by RiskEngine.
   - ARF_USE_HYPERPRIORS (default: `false`) — set to `true` to enable hyperprior behavior.
   - API_KEY (optional) — will populate `settings.api_key` but note that routes currently do not enforce authentication.
   - DATABASE_URL (optional) — configuration option in settings; tests use a local SQLite DB by default.

4. Run the app with Uvicorn for development:

   uvicorn app.main:app --reload --port 8000

   - The application mounts routes under the `/api/v1` prefix and exposes a health endpoint at `/health`.

Running tests

- Tests use an on-disk SQLite test database (`sqlite:///./test.db`) created by the test fixtures (`tests/conftest.py`).
- To run tests:

   pytest

- The test fixtures override the dependency that provides DB sessions so tests run against the test database.

Notes on the RiskEngine

- The app initializes a `RiskEngine` instance at startup (in `app.main`) using environment variables noted above. The engine instance is stored in `app.state.risk_engine` and is used by the governance endpoints.

Further development

- If you add persistent intent storage or authentication, update tests and dependency overrides accordingly.
