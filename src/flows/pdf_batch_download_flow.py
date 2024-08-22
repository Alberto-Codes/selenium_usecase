from prefect import flow, task

from src.db.db_connect import engine, get_session
from src.db.repositories.batch_repository import BatchRepository
from src.db.repositories.input_repository import InputRepository
from src.scrapers.pdf_site_scraper import PDFSiteScraper
from src.services.download_service import DownloadService
from src.utils.selenium_helper import WebAutomationHelper


@task
def process_records(records, download_service: DownloadService) -> None:
    """
    Processes multiple records by downloading the associated PDFs, handling any errors,
    and reusing the same browser window for all records.

    Args:
        records: The list of records containing the details for downloading the PDFs.
        download_service (DownloadService): The service used to download and store PDFs.

    Returns:
        None
    """
    with WebAutomationHelper() as helper:
        scraper = PDFSiteScraper(helper)

        for record in records:
            try:
                pdf_path = download_service.download_pdf(record, scraper)
                print(
                    f"Successfully downloaded and saved PDF for record {record.id} to {pdf_path}"
                )
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
        download_service = DownloadService(session)

        records = input_repo.get_records_by_batch_id(batch_id, limit)
        if not records:
            print(f"No pending records found for batch {batch_id}")
            return

        # Process all records in one go, using the same browser session
        process_records(records, download_service)

        batch_repo.update_batch_status(batch_id, "completed")
        print(f"Batch {batch_id} processing complete.")
    finally:
        session.close()
