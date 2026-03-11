# ARF API Control Plane

Welcome to the ARF API documentation.

Overview

- This repository implements the ARF API Control Plane (FastAPI) — the application mounts a number of routers under `/api/v1` and exposes a health endpoint at `/health`.
- App version (from app.main): 0.2.0

Important notes

- A `RiskEngine` is initialized at app startup and stored at `app.state.risk_engine`. The engine reads `ARF_HMC_MODEL` and `ARF_USE_HYPERPRIORS` environment variables.
- Authentication: there is an optional `api_key` in configuration, but request handlers do not currently enforce authentication.
- The `/api/v1/intents/outcome` endpoint exists but returns 501 Not Implemented; intent outcome recording/storage is not yet implemented.

See the other documentation pages for development instructions, endpoints, and examples.
