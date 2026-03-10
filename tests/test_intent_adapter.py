import pytest
from app.services.intent_adapter import to_oss_intent

class DummyRequest:
    intent_type = "UnknownIntent"

def test_unknown_intent_type():
    with pytest.raises(ValueError, match="Unknown intent type: UnknownIntent"):
        to_oss_intent(DummyRequest())
