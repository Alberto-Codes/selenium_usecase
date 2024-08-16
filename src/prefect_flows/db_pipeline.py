import os
import sys

from prefect import flow, task

from src.db.db_setup import create_database, destroy_database

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


@task
def create_db():
    """
    Task to create the database.

    Returns:
        sqlalchemy.engine.base.Engine: The SQLAlchemy engine connected to the
        database.
    """
    print("Creating database...")
    engine = create_database(echo=True)
    return engine


@task
def destroy_db():
    """
    Task to destroy the database by deleting the database file.
    """
    print("Destroying database...")
    db_path = "data/rcn.db"
    destroy_database(db_path)


@task
def check_db_exists():
    """
    Task to check if the database file exists.

    Returns:
        bool: True if the database file exists, False otherwise.
    """
    db_path = "data/rcn.db"
    return os.path.exists(db_path)


@flow
def db_management_flow(destroy=False):
    """
    Flow to manage database creation and destruction.

    Args:
        destroy (bool): If True, the database will be destroyed before
            attempting to create it. Defaults to False.
    """
    if destroy:
        destroy_db()

    db_exists = check_db_exists().result()

    if not db_exists:
        engine = create_db()
        print("Database created successfully.")
    else:
        print("Database already exists.")


if __name__ == "__main__":
    # Example usage: set destroy=True to destroy the DB first
    db_management_flow(destroy=False)
