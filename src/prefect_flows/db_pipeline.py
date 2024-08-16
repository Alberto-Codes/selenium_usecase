import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from prefect import flow, task

from src.db.db_setup import create_database, destroy_database


@task
def create_db():
    print("Creating database...")
    engine = create_database(echo=True)
    return engine


@task
def destroy_db():
    print("Destroying database...")
    db_path = "data/rcn.db"
    destroy_database(db_path)


@task
def check_db_exists():
    db_path = "data/rcn.db"
    return os.path.exists(db_path)


@flow
def db_management_flow(destroy=False):
    if destroy:
        destroy_db()

    db_exists = check_db_exists()

    if not db_exists:
        engine = create_db()
        print("Database created successfully.")
    else:
        print("Database already exists.")


if __name__ == "__main__":
    # Example usage: set destroy=True to destroy the DB first
    db_management_flow(destroy=False)
