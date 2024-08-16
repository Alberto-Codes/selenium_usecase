import pandas as pd
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from src.db.db_setup import TblRCNInput, get_session


def ensure_database_exists(engine):
    """
    Ensure the database connection is valid. If the database doesn't exist,
    this will raise an error.

    Args:
        engine (sqlalchemy.engine.base.Engine): The SQLAlchemy engine connected to the database.
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
    except OperationalError:
        raise RuntimeError("Database does not exist or is not accessible.")


def load_input_data(session: Session, input_data: pd.DataFrame):
    """
    Load the initial input data into the TblRCNInput table.

    Args:
        session (sqlalchemy.orm.Session): The SQLAlchemy session for database operations.
        input_data (pd.DataFrame): The input data to load, expected to have the following columns:
            - guid: str
            - account_number: str
            - check_number: str
            - amount: float
            - payee: str
            - issue_date: str (format: YYYY-MM-DD)
            - status: str
    """
    for index, row in input_data.iterrows():
        record = TblRCNInput(
            guid=row["guid"],
            account_number=row["account_number"],
            check_number=row["check_number"],
            amount=row["amount"],
            payee=row["payee"],
            issue_date=row["issue_date"],
            status=row.get("status", "pending"),
        )
        session.add(record)
    session.commit()


def load_data_from_excel(session: Session, file_path: str, sheet_name: str = None):
    """
    Load data from an Excel file into the TblRCNInput table.

    Args:
        session (sqlalchemy.orm.Session): The SQLAlchemy session for database operations.
        file_path (str): The path to the Excel file.
        sheet_name (str): The sheet name to load data from, default is None which loads the first sheet.
    """
    input_data = pd.read_excel(file_path, sheet_name=sheet_name)
    load_input_data(session, input_data)
