import datetime
from sqlalchemy.orm import Session
from app.database.models_intents import IntentDB
from typing import Any, Dict, Optional

def save_evaluated_intent(
    db: Session,
    deterministic_id: str,
    intent_type: str,
    api_payload: Dict[str, Any],
    oss_payload: Dict[str, Any],
    environment: str,
    risk_score: float
) -> IntentDB:
    existing = db.query(IntentDB).filter(IntentDB.deterministic_id == deterministic_id).one_or_none()
    if existing:
        existing.evaluated_at = datetime.datetime.utcnow()
        existing.risk_score = str(risk_score)
        existing.oss_payload = oss_payload
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    intent = IntentDB(
        deterministic_id=deterministic_id,
        intent_type=intent_type,
        payload=api_payload,
        oss_payload=oss_payload,
        environment=environment,
        evaluated_at=datetime.datetime.utcnow(),
        risk_score=str(risk_score)
    )
    db.add(intent)
    db.commit()
    db.refresh(intent)
    return intent

def get_intent_by_deterministic_id(db: Session, deterministic_id: str) -> Optional[IntentDB]:
    return db.query(IntentDB).filter(IntentDB.deterministic_id == deterministic_id).one_or_none()
