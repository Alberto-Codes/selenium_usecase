import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError, DBAPIError
from src.db.setup import setup_local_db, Base
# from src.db.models import Base

@pytest.fixture
def mock_engine():
    return MagicMock()

def test_setup_local_db_without_provided_engine(mock_engine):
    """
    Test setup_local_db when no engine is provided, so it defaults to get_engine().
    """
    with patch('src.db.setup.get_engine', return_value=mock_engine) as mock_get_engine, \
         patch.object(Base.metadata, 'create_all') as mock_create_all:
        
        setup_local_db()

        mock_get_engine.assert_called_once()
        mock_create_all.assert_called_once_with(bind=mock_engine)

def test_setup_local_db_engine_raises_exception(mock_engine):
    """
    Test setup_local_db when an OperationalError is raised during table creation.
    """
    with patch.object(Base.metadata, 'create_all', side_effect=OperationalError("statement", "params", "orig")) as mock_create_all:
        with pytest.raises(OperationalError):
            setup_local_db(engine=mock_engine)
