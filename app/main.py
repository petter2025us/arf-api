from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.api import routes_incidents, routes_risk, routes_intents, routes_history, routes_governance
from app.core.config import settings
from app.api.deps import limiter
from agentic_reliability_framework.core.governance.risk_engine import RiskEngine
import os
import sys

print(">>> Starting ARF API application...", flush=True)
print(f">>> sys.path: {sys.path}", flush=True)

app = FastAPI(title="ARF API Control Plane", version="0.3.0")
print(">>> FastAPI app created.", flush=True)

# --------------------------------------------------------------------------
# CORS configuration – allow your frontend domain
# --------------------------------------------------------------------------
ALLOWED_ORIGINS = [
    "https://arf-frontend-sandy.vercel.app",   # production frontend
    # "http://localhost:3000",                  # for local development (optional)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print(">>> CORS middleware configured.", flush=True)

# Set up rate limiter
app.state.limiter = limiter
# The following line may show a Pylance type warning, but it's safe to ignore.
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore
app.add_middleware(SlowAPIMiddleware)
print(">>> Rate limiter configured.", flush=True)

# Initialize RiskEngine (once)
hmc_model_path = os.getenv("ARF_HMC_MODEL", "models/hmc_model.json")
use_hyperpriors = os.getenv("ARF_USE_HYPERPRIORS", "false").lower() == "true"
print(f">>> Initializing RiskEngine with hmc_model_path={hmc_model_path}, use_hyperpriors={use_hyperpriors}", flush=True)
try:
    app.state.risk_engine = RiskEngine(
        hmc_model_path=hmc_model_path,
        use_hyperpriors=use_hyperpriors,
        n0=1000,
        hyperprior_weight=0.3
    )
    print(">>> RiskEngine initialized successfully.", flush=True)
except Exception as e:
    print(f">>> ERROR initializing RiskEngine: {e}", flush=True)
    raise

# Include routers
app.include_router(routes_incidents.router, prefix="/api/v1", tags=["incidents"])
app.include_router(routes_risk.router, prefix="/api/v1", tags=["risk"])
app.include_router(routes_intents.router, prefix="/api/v1", tags=["intents"])
app.include_router(routes_history.router, prefix="/api/v1", tags=["history"])
app.include_router(routes_governance.router, prefix="/api/v1", tags=["governance"])
print(">>> Routers included.", flush=True)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)
print(">>> Prometheus instrumentator configured.", flush=True)

@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}