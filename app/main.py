from fastapi import FastAPI
from app.api import routes_incidents, routes_risk, routes_intents, routes_history, routes_governance
from app.core.config import settings
from agentic_reliability_framework.core.governance.risk_engine import RiskEngine
import os

app = FastAPI(title="ARF API Control Plane", version="0.2.0")

# Initialize RiskEngine (once)
hmc_model_path = os.getenv("ARF_HMC_MODEL", "models/hmc_model.json")
use_hyperpriors = os.getenv("ARF_USE_HYPERPRIORS", "false").lower() == "true"
app.state.risk_engine = RiskEngine(
    hmc_model_path=hmc_model_path,
    use_hyperpriors=use_hyperpriors,
    n0=1000,
    hyperprior_weight=0.3
)

# Include routers
app.include_router(routes_incidents.router, prefix="/api/v1", tags=["incidents"])
app.include_router(routes_risk.router, prefix="/api/v1", tags=["risk"])
app.include_router(routes_intents.router, prefix="/api/v1", tags=["intents"])
app.include_router(routes_history.router, prefix="/api/v1", tags=["history"])
app.include_router(routes_governance.router, prefix="/api/v1", tags=["governance"])

@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
