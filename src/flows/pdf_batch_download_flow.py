from prefect import flow, task

from src.db.db_connect import engine, get_session
from src.db.repositories.batch_repository import BatchRepository
from src.db.repositories.input_repository import InputRepository
from src.scrapers.pdf_site_scraper import PDFSiteScraper
from src.services.download_service import DownloadService
from src.utils.selenium_helper import WebAutomationHelper


@task
def process_records(
    records, download_service: DownloadService, scraper: PDFSiteScraper
) -> None:
    """
    Processes multiple records by downloading the associated PDFs and handling any errors.

    Args:
        records: The records containing the details for downloading the PDFs.
        download_service (DownloadService): The service used to download and store PDFs.
        scraper (PDFSiteScraper): Scraper class to execute the web download steps.

    Returns:
        None
    """
    for record in records:
        try:
            download_service.process_row_for_download(record, scraper)
            print(f"Successfully downloaded and saved PDF for record {record.id}")
        except Exception as e:
            print(f"Failed to download for record {record.id}: {e}")


@flow
def pdf_batch_download_flow(batch_id: str, limit: int = 10) -> None:
    """
    Main flow to download PDFs for a batch of records, reusing the browser window.

    Args:
        batch_id (str): The ID of the batch to process.
        limit (int): The maximum number of records to process. Defaults to 10.

    Returns:
        None
    """
    session = get_session(engine)
    try:
        input_repo = InputRepository(session)
        batch_repo = BatchRepository(session)
        records = input_repo.get_records_by_batch_id(batch_id, limit)
        if not records:
            print(f"No pending records found for batch {batch_id}")
            return

        # Initialize the WebAutomationHelper (and the browser session) once
        helper = WebAutomationHelper()
        try:
            scraper = PDFSiteScraper(helper)
            download_service = DownloadService(session, helper)

            # Process all records in the batch
            process_records(records, download_service, scraper)

        finally:
            helper.quit()  # Ensure the browser session is closed
        batch_repo.update_batch_status(batch_id, "completed")
        print(f"Batch {batch_id} processing complete.")
    finally:
        session.close()
