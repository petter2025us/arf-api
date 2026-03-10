import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.database.models_intents import IntentDB, OutcomeDB
from app.services.outcome_service import record_outcome, OutcomeConflictError
from unittest.mock import MagicMock
import datetime
from agentic_reliability_framework.core.governance.intents import (
    ProvisionResourceIntent,
    ResourceType,
)

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, future=True)
    Base.metadata.create_all(bind=engine)
    sess = TestingSessionLocal()
    yield sess
    sess.close()

@pytest.fixture
def mock_risk_engine():
    engine = MagicMock()
    engine.update_outcome = MagicMock()
    return engine

def test_record_outcome_creates_row_and_updates_engine(db_session, mock_risk_engine):
    # Create a real OSS intent with dummy values
    oss_intent = ProvisionResourceIntent(
        resource_type=ResourceType.VM,
        region="eastus",
        size="Standard",
        environment="dev",  # use string literal, not enum
        requester="test_user"
    )
    # Use mode='json' to convert datetime to string automatically
    oss_payload = oss_intent.model_dump(mode='json')

    intent = IntentDB(
        deterministic_id="intent_abc",
        intent_type="ProvisionResourceIntent",
        payload={},
        oss_payload=oss_payload,
        created_at=datetime.datetime.utcnow()
    )
    db_session.add(intent)
    db_session.commit()
    db_session.refresh(intent)

    outcome = record_outcome(
        db=db_session,
        deterministic_id="intent_abc",
        success=True,
        recorded_by="tester",
        notes="works",
        risk_engine=mock_risk_engine
    )
    assert outcome.success is True
    assert outcome.recorded_by == "tester"
    mock_risk_engine.update_outcome.assert_called_once()

    outcome2 = record_outcome(
        db=db_session,
        deterministic_id="intent_abc",
        success=True,
        recorded_by="tester",
        notes="again",
        risk_engine=mock_risk_engine
    )
    assert outcome2.id == outcome.id
    mock_risk_engine.update_outcome.assert_called_once()

def test_conflict_different_result(db_session, mock_risk_engine):
    intent = IntentDB(
        deterministic_id="intent_def",
        intent_type="ProvisionResourceIntent",
        payload={},
        created_at=datetime.datetime.utcnow()
    )
    db_session.add(intent)
    db_session.commit()

    record_outcome(db_session, "intent_def", True, None, None, mock_risk_engine)
    with pytest.raises(OutcomeConflictError):
        record_outcome(db_session, "intent_def", False, None, None, mock_risk_engine)

def test_nonexistent_intent(db_session, mock_risk_engine):
    with pytest.raises(ValueError):
        record_outcome(db_session, "missing", True, None, None, mock_risk_engine)

def test_record_outcome_reconstruction_fallback(db_session, mock_risk_engine):
    # Create an intent with an invalid oss_payload (missing required fields)
    intent = IntentDB(
        deterministic_id="intent_bad",
        intent_type="ProvisionResourceIntent",
        payload={},
        oss_payload={"intent_type": "provision_resource"},  # missing required fields
        created_at=datetime.datetime.utcnow()
    )
    db_session.add(intent)
    db_session.commit()
    db_session.refresh(intent)

    # This should not raise, and should fall back to dummy intent
    outcome = record_outcome(
        db=db_session,
        deterministic_id="intent_bad",
        success=True,
        recorded_by="tester",
        notes="fallback test",
        risk_engine=mock_risk_engine
    )
    assert outcome.success is True
    # The engine update should still be called (dummy intent used)
    mock_risk_engine.update_outcome.assert_called_once()
