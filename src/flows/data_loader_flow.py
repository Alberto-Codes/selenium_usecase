from prefect import flow, task
from sqlalchemy.orm import Session

from src.db.db_connect import get_session
from src.services.data_loader_service import DataLoaderService


@task
def load_data_task(session: Session, spreadsheet_path: str) -> None:
    """
    Task to load data into the database using DataLoaderService.

    Args:
        session (Session): The SQLAlchemy session for database operations.
        spreadsheet_path (str): The file path to the spreadsheet containing the data to be loaded.

    Returns:
        None
    """
    data_loader = DataLoaderService(session)
    data_loader.load_dataset_into_db(spreadsheet_path)


@flow
def data_loader_flow(spreadsheet_path: str) -> None:
    """
    Prefect flow to manage the data loading process.

    Args:
        spreadsheet_path (str): The file path to the spreadsheet containing the data to be loaded.

    Returns:
        None
    """
    session = get_session()
    load_data_task(session, spreadsheet_path).result()
    session.close()


if __name__ == "__main__":
    # Run the flow with the path to the spreadsheet
    data_loader_flow("path/to/your/spreadsheet.xlsx")
