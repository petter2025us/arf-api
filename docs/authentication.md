# Authentication

This page describes how to authenticate with the ARF API.

Current status

- There is no route-level or global authentication enforced by the API code in this repository. The API routes (including governance endpoints) do not validate API keys, tokens, or other credentials.

What the code provides

- The configuration model (app/core/config.py) exposes an optional `api_key` setting. This can be provided via environment variables or a `.env` file (the BaseSettings `env_file` is configured to read `.env`).

What this means for you

- Setting `API_KEY` in a `.env` file or environment variable will populate the `settings.api_key`, but the current route implementations do not check this value.
- If you require authentication, add a FastAPI dependency or middleware that checks `settings.api_key` (or another auth mechanism) and then apply it to routes or include it in a dependency override.

Suggested minimal approach to enable API key checking

- Implement a dependency in `app.api.deps` (e.g., `get_api_key`) that compares a header value to `settings.api_key` and raise `HTTPException(401)` when missing/invalid.
- Add that dependency to routers or individual endpoints where auth is required.

Notes

- Tests and example code in this repo currently run without auth.
