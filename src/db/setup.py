from sqlalchemy.orm import declarative_base
from src.db.connect import get_engine

# Base for the local DuckDB database
Base = declarative_base()

def setup_local_db(engine=None):
    """
    Set up the database schema for the local DuckDB instance.
    
    This function initializes the tables in the local DuckDB instance. It 
    uses the SQLAlchemy `Base` metadata to create all defined tables. If an 
    engine is not provided, it will retrieve the default engine using 
    `get_engine()`.

    Args:
        engine (sqlalchemy.engine.Engine, optional): The SQLAlchemy engine 
        instance to bind with the metadata. Defaults to None.

    Returns:
        None
    """
    if engine is None:
        engine = get_engine()
    
    # Create all tables in the local DuckDB instance
    Base.metadata.create_all(bind=engine)

def setup_online_db(engine=None):
    """
    Placeholder for setting up the online database.
    
    This function is not implemented yet but provides a framework for future
    expansion when the online database is integrated. It accepts an engine 
    parameter for consistency but currently does nothing.

    Args:
        engine (sqlalchemy.engine.Engine, optional): The SQLAlchemy engine 
        instance intended for the online database. Defaults to None.

    Returns:
        None
    """
    pass  # Implement this when you introduce the online database
