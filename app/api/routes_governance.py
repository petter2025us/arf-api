from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.models.infrastructure_intents import InfrastructureIntentRequest
from app.services.intent_adapter import to_oss_intent
from app.services.risk_service import evaluate_intent
from app.services.intent_store import save_evaluated_intent
from app.services.outcome_service import record_outcome
from app.api.deps import get_db
from pydantic import BaseModel
import uuid

router = APIRouter()

class OutcomeRequest(BaseModel):
    deterministic_id: str
    success: bool
    recorded_by: str
    notes: str = ""


@router.post("/intents/evaluate")
async def evaluate_intent_endpoint(
    request: Request,
    intent_req: InfrastructureIntentRequest,
    db: Session = Depends(get_db)
):
    """
    Evaluate an infrastructure intent, store it, and return risk score + explanation + intent ID.
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

        # Generate a deterministic ID (could use hash of payload, but simple UUID for now)
        deterministic_id = str(uuid.uuid4())

        # Store the intent - ensure JSON serializable
        api_payload = jsonable_encoder(intent_req.model_dump())
        oss_payload = jsonable_encoder(oss_intent.model_dump())

        save_evaluated_intent(
            db=db,
            deterministic_id=deterministic_id,
            intent_type=intent_req.intent_type,  # string literal, not enum
            api_payload=api_payload,
            oss_payload=oss_payload,
            environment=str(intent_req.environment),  # convert enum to string
            risk_score=result["risk_score"]
        )

        # Add the intent ID to the response
        result["intent_id"] = deterministic_id
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intents/outcome")
async def record_outcome_endpoint(
    request: Request,
    outcome: OutcomeRequest,
    db: Session = Depends(get_db)
):
    """
    Record the outcome of an executed intent to update Bayesian priors.
    """
    try:
        risk_engine = request.app.state.risk_engine
        outcome_record = record_outcome(
            db=db,
            deterministic_id=outcome.deterministic_id,
            success=outcome.success,
            recorded_by=outcome.recorded_by,
            notes=outcome.notes,
            risk_engine=risk_engine
        )
        return {"message": "Outcome recorded", "outcome_id": outcome_record.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
