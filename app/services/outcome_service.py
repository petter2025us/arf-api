import datetime
import logging
from sqlalchemy.orm import Session
from app.database.models_intents import IntentDB, OutcomeDB
from typing import Optional, Dict, Any
from agentic_reliability_framework.core.governance.risk_engine import RiskEngine
from agentic_reliability_framework.core.governance.intents import (
    InfrastructureIntent,
    ProvisionResourceIntent,
    GrantAccessIntent,
    DeployConfigurationIntent,
)

logger = logging.getLogger(__name__)

class OutcomeConflictError(Exception):
    pass

def reconstruct_oss_intent_from_json(oss_json: Dict[str, Any]) -> InfrastructureIntent:
    intent_type = oss_json.get("intent_type")
    if intent_type == "provision_resource":
        return ProvisionResourceIntent(**oss_json)
    elif intent_type == "grant_access":
        return GrantAccessIntent(**oss_json)
    elif intent_type == "deploy_config":
        return DeployConfigurationIntent(**oss_json)
    else:
        raise ValueError(f"Cannot reconstruct intent from JSON: missing or unknown intent_type {intent_type}")

def dummy_intent_for_category(category: str) -> InfrastructureIntent:
    from agentic_reliability_framework.core.governance.intents import ProvisionResourceIntent, Environment
    return ProvisionResourceIntent(
        resource_type="VM",
        region="dummy",
        size="dummy",
        environment="dev",
        requester="system"
    )

def record_outcome(
    db: Session,
    deterministic_id: str,
    success: bool,
    recorded_by: Optional[str],
    notes: Optional[str],
    risk_engine: RiskEngine
) -> OutcomeDB:
    intent = db.query(IntentDB).filter(IntentDB.deterministic_id == deterministic_id).one_or_none()
    if not intent:
        raise ValueError(f"Intent not found: {deterministic_id}")

    existing_outcome = db.query(OutcomeDB).filter(OutcomeDB.intent_id == intent.id).one_or_none()
    if existing_outcome:
        if existing_outcome.success == success:
            return existing_outcome
        raise OutcomeConflictError("Outcome already recorded with different result")

    outcome = OutcomeDB(
        intent_id=intent.id,
        success=bool(success),
        recorded_by=recorded_by,
        notes=notes,
        recorded_at=datetime.datetime.utcnow()
    )
    db.add(outcome)
    db.commit()
    db.refresh(outcome)

    try:
        if intent.oss_payload:
            oss_intent = reconstruct_oss_intent_from_json(intent.oss_payload)
        else:
            oss_intent = dummy_intent_for_category(intent.environment or "default")
        risk_engine.update_outcome(oss_intent, success)
    except Exception as e:
        logger.exception("Failed to update RiskEngine after recording outcome for intent %s: %s", deterministic_id, e)

    return outcome
