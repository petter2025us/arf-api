import random
import logging
from agentic_reliability_framework.core.governance.risk_engine import RiskEngine
from app.models.intent_models import IntentSimulation

logger = logging.getLogger(__name__)

# Note: This endpoint is deprecated. Use /v1/intents/evaluate instead.
def simulate_intent(intent: IntentSimulation) -> dict:
    logger.warning("Deprecated endpoint /simulate_intent used. Please migrate to /v1/intents/evaluate.")
    # For backward compatibility, we still use random risk.
    risk_score = random.uniform(0, 1)
    if risk_score < 0.2:
        recommendation = "safe_to_execute"
    elif risk_score < 0.6:
        recommendation = "requires_approval"
    else:
        recommendation = "blocked"
    return {"risk_score": risk_score, "recommendation": recommendation}
