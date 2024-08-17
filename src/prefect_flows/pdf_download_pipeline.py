from prefect import flow, task
from sqlalchemy.orm import Session
from src.db.db_setup import get_session
from src.download_manager import process_rows_for_download

@task
def download_pdfs_task(db_path: str = "data/rcn.db"):
    """
    Task to download PDFs for pending records in the database.
    
    Args:
        db_path (str): Path to the DuckDB database.
    """
    session = get_session(db_path=db_path)
    process_rows_for_download(session)

@flow
def download_pdf_flow():
    """
    Prefect flow to handle downloading PDFs for pending records in batches.
    """
    download_pdfs_task()

if __name__ == "__main__":
    download_pdf_flow()
