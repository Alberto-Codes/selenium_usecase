from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from teradatasqlalchemy import TeradataDialect
from typing import Optional
import os
import keyring
from dotenv import load_dotenv
from contextlib import contextmanager
from urllib.parse import quote_plus
from typing import Generator

load_dotenv()


class DatabaseManager:
    """
    Manages connections and sessions for Teradata and DuckDB databases.
    Uses keyring for credential management, which interfaces with
    Windows Credential Manager on Windows systems.

    Usage:
        db_manager = DatabaseManager()
        db_manager.initialize_teradata()
        db_manager.initialize_duckdb()

        # Using Teradata
        with db_manager.get_teradata_session() as session:
            # Perform database operations

        # Using DuckDB
        with db_manager.get_duckdb_session() as session:
            # Perform database operations

        # Clean up
        db_manager.quit()
    """

    def __init__(self):
        """
        Initializes the DatabaseManager with no active database connections.
        """
        self.teradata_engine: Optional[Engine] = None
        self.duckdb_engine: Optional[Engine] = None
        self.TeradataSession = None
        self.DuckDBSession = None

    def initialize_teradata(self) -> None:
        """
        Initializes the Teradata SQLAlchemy engine and session factory.

        This method retrieves the Teradata hostname and database from
        environment variables, and the username and password from the
        system's keyring.

        Before calling this method, ensure that:
        1. The following environment variables are set:
           - TERADATA_HOSTNAME
           - TERADATA_DATABASE
        2. The Teradata credentials are stored in the keyring:
           keyring.set_password("ABCD", "username", "your_username")
           keyring.set_password("ABCD", "password", "your_password")

        Raises:
            ValueError: If Teradata configuration is not set in environment
                variables or if the credentials are not found in the keyring.
        """
        hostname = os.getenv("TERADATA_HOSTNAME")
        database = os.getenv("TERADATA_DATABASE")

        if not all([hostname, database]):
            raise ValueError(
                "Teradata hostname or database not properly set in "
                "environment variables."
            )

        # Retrieve credentials from keyring
        username = keyring.get_password("ABCD", "username")
        password = keyring.get_password("ABCD", "password")

        if not username or not password:
            raise ValueError("Teradata credentials not found in keyring under 'ABCD'.")

        # Construct the connection URL with LDAP authentication
        connection_url = (
            f"teradatasql://{quote_plus(username)}:{quote_plus(password)}"
            f"@{hostname}/?database={database}&authentication=LDAP&logmech=LDAP"
        )

        self.teradata_engine = create_engine(
            connection_url,
            dialect=TeradataDialect(),
            connect_args={"authentication": "LDAP", "logmech": "LDAP"},
        )
        self.TeradataSession = sessionmaker(bind=self.teradata_engine)

    def initialize_duckdb(self, db_path: str = "data/rcn.db") -> None:
        """
        Initializes the DuckDB SQLAlchemy engine and session factory.

        Args:
            db_path (str): The path to the DuckDB database file.

        Usage:
            db_manager.initialize_duckdb()
            # or
            db_manager.initialize_duckdb("path/to/your/database.db")
        """
        self.duckdb_engine = create_engine(f"duckdb:///{db_path}")
        self.DuckDBSession = sessionmaker(bind=self.duckdb_engine)

    @contextmanager
    def get_teradata_session(self) -> Generator[Session, None, None]:
        """
        Provides a context manager for a Teradata session.

        Usage:
            with db_manager.get_teradata_session() as session:
                # Perform database operations
                result = session.execute("SELECT * FROM your_table")
                for row in result:
                    print(row)

        Yields:
            Session: A SQLAlchemy session connected to Teradata.

        Raises:
            RuntimeError: If the Teradata engine is not initialized.
        """
        if not self.TeradataSession:
            raise RuntimeError(
                "Teradata engine not initialized. Call initialize_teradata() " "first."
            )
        session = self.TeradataSession()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def get_duckdb_session(self) -> Generator[Session, None, None]:
        """
        Provides a context manager for a DuckDB session.

        Usage:
            with db_manager.get_duckdb_session() as session:
                # Perform database operations
                session.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER, "
                                "name TEXT)")
                session.execute("INSERT INTO test VALUES (1, 'example')")
                result = session.execute("SELECT * FROM test")
                for row in result:
                    print(row)

        Yields:
            Session: A SQLAlchemy session connected to DuckDB.

        Raises:
            RuntimeError: If the DuckDB engine is not initialized.
        """
        if not self.DuckDBSession:
            raise RuntimeError(
                "DuckDB engine not initialized. Call initialize_duckdb() first."
            )
        session = self.DuckDBSession()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def quit(self):
        """
        Disposes of the database engines if they are initialized.

        This method should be called when you're done using the DatabaseManager
        to properly release all database resources.

        Usage:
            db_manager = DatabaseManager()
            # ... use the database manager ...
            db_manager.quit()
        """
        if self.teradata_engine:
            self.teradata_engine.dispose()
        if self.duckdb_engine:
            self.duckdb_engine.dispose()
