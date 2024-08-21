import os
import re
import sys

import pytest
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from db.db_manager import DatabaseManager


@pytest.fixture
def db_manager():
    """Fixture for providing a DatabaseManager instance."""
    return DatabaseManager()


def test_initialize_teradata(db_manager, mocker):
    """Test the initialization of Teradata engine and session.

    This test verifies that the Teradata engine and session are properly
    initialized when the required environment variables and credentials are
    provided.

    Args:
        db_manager (DatabaseManager): The database manager instance.
        mocker (MockerFixture): The mocker fixture for patching.

    Patches:
        os.getenv: Returns 'mock_value' for required Teradata environment
            variables.
        keyring.get_password: Returns 'mock_password'.
        sqlalchemy.create_engine: Mocked to simulate engine creation.
    """
    mocker.patch(
        "os.getenv",
        side_effect=lambda key: "mock_value"
        if key in ["TERADATA_HOSTNAME", "TERADATA_DATABASE"]
        else None,
    )
    mocker.patch("keyring.get_password", return_value="mock_password")
    mocker.patch("sqlalchemy.create_engine")
    db_manager.initialize_teradata()
    assert db_manager.teradata_engine is not None
    assert db_manager.TeradataSession is not None


def test_initialize_teradata_missing_env_vars(db_manager, mocker):
    """Test Teradata initialization with missing environment variables.

    This test ensures that the proper error is raised when the required
    Teradata environment variables are not set.

    Args:
        db_manager (DatabaseManager): The database manager instance.
        mocker (MockerFixture): The mocker fixture for patching.

    Patches:
        os.getenv: Returns None to simulate missing environment variables.

    Raises:
        ValueError: When Teradata hostname or database environment variables
            are not set.
    """
    mocker.patch("os.getenv", return_value=None)
    with pytest.raises(
        ValueError,
        match="Teradata hostname or database not properly set in environment variables.",
    ):
        db_manager.initialize_teradata()


def test_initialize_teradata_missing_credentials(db_manager, mocker):
    """Test Teradata initialization with missing credentials.

    This test ensures that the proper error is raised when the required
    Teradata credentials are not found in the keyring.

    Args:
        db_manager (DatabaseManager): The database manager instance.
        mocker (MockerFixture): The mocker fixture for patching.

    Patches:
        os.getenv: Returns 'mock_value' for required Teradata environment
            variables.
        keyring.get_password: Returns None to simulate missing credentials.

    Raises:
        ValueError: When Teradata credentials are not found in the keyring.
    """
    mocker.patch(
        "os.getenv",
        side_effect=lambda key: "mock_value"
        if key in ["TERADATA_HOSTNAME", "TERADATA_DATABASE"]
        else None,
    )
    mocker.patch("keyring.get_password", return_value=None)
    with pytest.raises(
        ValueError, match="Teradata credentials not found in keyring under 'ABCD'."
    ):
        db_manager.initialize_teradata()


def test_initialize_duckdb(db_manager, mocker):
    """Test the initialization of DuckDB engine and session.

    This test verifies that the DuckDB engine and session are properly
    initialized.

    Args:
        db_manager (DatabaseManager): The database manager instance.
        mocker (MockerFixture): The mocker fixture for patching.

    Patches:
        sqlalchemy.create_engine: Mocked to simulate engine creation.
    """
    mocker.patch("sqlalchemy.create_engine")
    db_manager.initialize_duckdb()
    assert db_manager.duckdb_engine is not None
    assert db_manager.DuckDBSession is not None


def test_get_teradata_session(db_manager, mocker):
    """Test retrieving a Teradata session.

    This test verifies that a Teradata session can be retrieved
    successfully if the Teradata engine has been initialized.

    Args:
        db_manager (DatabaseManager): The database manager instance.
        mocker (MockerFixture): The mocker fixture for patching.

    Patches:
        DatabaseManager.TeradataSession: Mocked to return a session instance.

    Asserts:
        The session retrieved is an instance of `sqlalchemy.orm.Session`.
    """
    mocker.patch.object(
        db_manager, "TeradataSession", return_value=mocker.Mock(spec=Session)
    )
    with db_manager.get_teradata_session() as session:
        assert isinstance(session, Session)


def test_get_teradata_session_not_initialized(db_manager):
    """Test retrieving Teradata session without initializing the engine.

    This test ensures that an error is raised if the Teradata engine has
    not been initialized before attempting to retrieve a session.

    Args:
        db_manager (DatabaseManager): The database manager instance.

    Raises:
        RuntimeError: When Teradata engine is not initialized.
    """
    with pytest.raises(
        RuntimeError,
        match=re.escape(
            "Teradata engine not initialized. Call initialize_teradata() first."
        ),
    ):
        with db_manager.get_teradata_session():
            pass


def test_get_duckdb_session(db_manager, mocker):
    """Test retrieving a DuckDB session.

    This test verifies that a DuckDB session can be retrieved successfully
    if the DuckDB engine has been initialized.

    Args:
        db_manager (DatabaseManager): The database manager instance.
        mocker (MockerFixture): The mocker fixture for patching.

    Patches:
        DatabaseManager.DuckDBSession: Mocked to return a session instance.

    Asserts:
        The session retrieved is an instance of `sqlalchemy.orm.Session`.
    """
    mocker.patch.object(
        db_manager, "DuckDBSession", return_value=mocker.Mock(spec=Session)
    )
    with db_manager.get_duckdb_session() as session:
        assert isinstance(session, Session)


def test_get_duckdb_session_not_initialized(db_manager):
    """Test retrieving DuckDB session without initializing the engine.

    This test ensures that an error is raised if the DuckDB engine has not
    been initialized before attempting to retrieve a session.

    Args:
        db_manager (DatabaseManager): The database manager instance.

    Raises:
        RuntimeError: When DuckDB engine is not initialized.
    """
    with pytest.raises(
        RuntimeError,
        match=re.escape(
            "DuckDB engine not initialized. Call initialize_duckdb() first."
        ),
    ):
        with db_manager.get_duckdb_session():
            pass


def test_quit(db_manager, mocker):
    """Test quitting the database manager.

    This test verifies that the Teradata and DuckDB engines are properly
    disposed of when the `quit` method is called.

    Args:
        db_manager (DatabaseManager): The database manager instance.
        mocker (MockerFixture): The mocker fixture for patching.

    Patches:
        DatabaseManager.teradata_engine: Mocked to verify disposal.
        DatabaseManager.duckdb_engine: Mocked to verify disposal.

    Asserts:
        Both Teradata and DuckDB engines are disposed of exactly once.
    """
    mock_teradata_engine = mocker.Mock()
    mock_duckdb_engine = mocker.Mock()
    db_manager.teradata_engine = mock_teradata_engine
    db_manager.duckdb_engine = mock_duckdb_engine
    db_manager.quit()
    mock_teradata_engine.dispose.assert_called_once()
    mock_duckdb_engine.dispose.assert_called_once()
