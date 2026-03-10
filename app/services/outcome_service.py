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

def _create_dummy_intent(intent_type: str) -> Optional[InfrastructureIntent]:
    """Create a valid dummy intent for a given intent type.
    For now, only ProvisionResourceIntent is fully supported.
    """
    from agentic_reliability_framework.core.governance.intents import (
        ProvisionResourceIntent,
    )
    if intent_type == "ProvisionResourceIntent":
        # Use string values directly; they must be valid according to the model
        return ProvisionResourceIntent(
            resource_type="vm",
            region="eastus",
            size="Standard_D2s_v3",
            environment="dev",          # Use string instead of Environment.dev
            requester="system"
        )
    else:
        logger.warning("Dummy intent creation not implemented for %s", intent_type)
        return None

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
        recorded_at=datetime.datetime.utcnow()  # will be replaced with timezone-aware later
    )
    db.add(outcome)
    db.commit()
    db.refresh(outcome)

    # Determine OSS intent for risk engine update
    oss_intent = None
    if intent.oss_payload:
        try:
            oss_intent = reconstruct_oss_intent_from_json(intent.oss_payload)
        except Exception as e:
            logger.warning("Failed to reconstruct OSS intent for %s: %s. Using dummy fallback.", deterministic_id, e)
            oss_intent = _create_dummy_intent(intent.intent_type)
    else:
        oss_intent = _create_dummy_intent(intent.intent_type)

    # Update risk engine if we have an intent
    if oss_intent is not None:
        try:
            risk_engine.update_outcome(oss_intent, success)
        except Exception as e:
            logger.exception("Failed to update RiskEngine after recording outcome for intent %s: %s", deterministic_id, e)
    else:
        logger.error("No valid OSS intent available for risk engine update; skipping outcome for %s", deterministic_id)

    return outcome
