from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session


def get_engine(db_path: str = "data/rcn.db", echo: bool = False) -> Engine:
    """
    Creates and returns a SQLAlchemy engine.

    Args:
        db_path (str): Path to the database. Defaults to "data/rcn.db".
        echo (bool): If True, SQLAlchemy will log all the SQL statements.
            Defaults to False.

    Returns:
        Engine: SQLAlchemy engine connected to the database.
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
    Session = sessionmaker(bind=engine)
    return Session()


# Create the engine instance once, and use it throughout the application
engine = get_engine()

# Example usage of a session, which can be imported as well
session = get_session(engine)
