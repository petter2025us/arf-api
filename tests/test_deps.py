import pytest
from unittest.mock import patch, MagicMock
from app.api.deps import get_db

def test_get_db_closes_session():
    mock_session = MagicMock()
    with patch('app.api.deps.SessionLocal', return_value=mock_session):
        db_gen = get_db()
        db = next(db_gen)
        assert db == mock_session
        # Simulate an exception during request handling
        with pytest.raises(Exception):
            db_gen.throw(Exception("test error"))
        mock_session.close.assert_called_once()
