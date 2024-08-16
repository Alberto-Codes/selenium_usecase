from prefect import flow, task
from sqlalchemy import create_engine

from src.db.data_loader import ensure_database_exists, load_data_from_excel
from src.db.db_setup import get_session


@task
def connect_to_database(db_path: str):
    """
    Connect to an existing database and ensure it exists.

    Args:
        db_path (str): Path to the database file.

    Returns:
        sqlalchemy.orm.Session: The SQLAlchemy session for database operations.
    """
    engine = create_engine(f"duckdb:///{db_path}")
    ensure_database_exists(engine)
    session = get_session(engine)
    return session


@task
def load_input_data_task(session, file_path: str, sheet_name: str = None):
    """
    Task to load input data from an Excel file.

    Args:
        session (sqlalchemy.orm.Session): The SQLAlchemy session for database operations.
        file_path (str): Path to the Excel file.
        sheet_name (str): The sheet name to load data from, default is None which loads the first sheet.
    """
    load_data_from_excel(session, file_path, sheet_name)


@flow
def ocr_pipeline(file_path: str, db_path: str, sheet_name: str = None):
    """
    Main flow to run the OCR pipeline.

    Args:
        file_path (str): Path to the Excel file.
        db_path (str): Path to the database file.
        sheet_name (str): The sheet name to load data from, default is None which loads the first sheet.
    """
    session = connect_to_database(db_path)
    load_input_data_task(session, file_path, sheet_name)
    # Add more steps as needed...


if __name__ == "__main__":
    # Run the pipeline with the given Excel file path and database path
    ocr_pipeline(
        file_path="data/input_data.xlsx", db_path="data/rcn.db", sheet_name="Sheet1"
    )
