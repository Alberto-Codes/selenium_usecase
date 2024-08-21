"""
This module provides database connection utilities for DuckDB and Teradata.
It includes functions for creating SQLAlchemy engine instances and obtaining
database sessions, as well as defining the base models for ORM mapping.
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def get_duckdb_engine(db_path: str = "data/rcn.db", echo: bool = False) -> Engine:
    """
    Creates and returns a DuckDB SQLAlchemy engine.

    Args:
        db_path (str): The path to the DuckDB database file. Defaults to "data/rcn.db".
        echo (bool): If True, SQLAlchemy will log all SQL statements. Defaults to False.

    Returns:
        Engine: SQLAlchemy engine connected to DuckDB.
    """
    return create_engine(f"duckdb:///{db_path}", echo=echo)


def get_session(engine: Engine) -> Session:
    """
    Creates and returns a new SQLAlchemy session bound to the provided engine.

    Args:
        engine (Engine): The SQLAlchemy engine connected to the database.

    Returns:
        Session: A new session object for database operations.
    """
    session_factory = sessionmaker(bind=engine)
    return session_factory()


# Initialize DuckDB engine and session
duckdb_engine = get_duckdb_engine()
duckdb_session = get_session(duckdb_engine)
