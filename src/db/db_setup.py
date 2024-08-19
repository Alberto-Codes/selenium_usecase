import os

from sqlalchemy.ext.declarative import declarative_base

from src.db.db_connect import create_engine

Base = declarative_base()


def create_database(db_path: str = "data/rcn.db", echo: bool = False):
    """
    Creates the database and the tables defined in this module.

    Args:
        db_path (str): The path where the database file will be created.
            Defaults to 'data/rcn.db'.
        echo (bool): If True, SQLAlchemy will log all the SQL statements.
            Defaults to False.

    Returns:
        sqlalchemy.engine.base.Engine: The SQLAlchemy engine connected to the
        database.
    """
    engine = create_engine(f"duckdb:///{db_path}", echo=echo)
    Base.metadata.create_all(engine)
    return engine


def destroy_database(db_path: str = "data/rcn.db"):
    """
    Destroys the database by deleting the file.

    Args:
        db_path (str): The path where the database file is located.
            Defaults to 'data/rcn.db'.
    """
    if os.path.exists(db_path):
        os.remove(db_path)
