from fastapi import APIRouter, Depends, HTTPException, Request
from app.models.infrastructure_intents import InfrastructureIntentRequest
from app.services.intent_adapter import to_oss_intent
from app.services.risk_service import evaluate_intent
from pydantic import BaseModel

router = APIRouter()

class OutcomeRequest(BaseModel):
    intent_id: str
    success: bool


@router.post("/intents/evaluate")
async def evaluate_intent_endpoint(request: Request, intent_req: InfrastructureIntentRequest):
    """
    Evaluate an infrastructure intent and return risk score + explanation.
    """
    try:
        oss_intent = to_oss_intent(intent_req)
        # Get risk engine from app state
        risk_engine = request.app.state.risk_engine
        result = evaluate_intent(
            engine=risk_engine,
            intent=oss_intent,
            cost_estimate=intent_req.estimated_cost,
            policy_violations=intent_req.policy_violations
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intents/outcome")
async def record_outcome_endpoint(request: Request, outcome: OutcomeRequest):
    """
    Record the outcome of an executed intent to update Bayesian priors.
    """
    try:
        # In a real implementation, you would retrieve the intent from a database
        # using outcome.intent_id. For now, we assume the intent is passed as part of the request.
        # This endpoint is simplified; a full implementation would need intent storage.
        # We'll skip for now and log a warning.
        raise HTTPException(status_code=501, detail="Outcome recording not yet implemented (needs intent storage)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
