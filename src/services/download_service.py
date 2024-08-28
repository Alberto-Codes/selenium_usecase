import os
import shutil
import tempfile

from sqlalchemy.orm import Session

from src.db.repositories.input_repository import InputRepository
from src.db.repositories.pdf_repository import PDFRepository
from src.scrapers.pdf_site_scraper import PDFSiteScraper
from src.services.pdf_processing_service import PDFProcessingService


class DownloadService:
    """
    Service class for handling the download of PDFs and storing them in the database.
    """

    def __init__(self, session: Session, helper):
        """
        Initializes the DownloadService.

        Args:
            session (Session): The SQLAlchemy session for database operations.
            helper (WebAutomationHelper): The Selenium helper instance to keep
                the browser session alive.
        """
        self.pdf_repo = PDFRepository(session)
        self.input_repo = InputRepository(session)
        self.pdf_service = PDFProcessingService()
        self.helper = helper

    def process_row_for_download(self, row, scraper: PDFSiteScraper) -> None:
        """
        Processes a single row: downloads a PDF, saves it as a blob, moves and renames it,
        and stores the blob in the database.

        Args:
            row: The record containing details for downloading the PDF.
            scraper (PDFSiteScraper): The scraper to execute the web download steps.

        Returns:
            None
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Download the PDF into the temp directory
                pdf_path = self.download_pdf(row, scraper, temp_dir)
                if not os.path.exists(pdf_path):
                    raise FileNotFoundError(
                        f"No PDF file was found for record {row.id}"
                    )

                # Save the PDF blob to the database before any further processing
                with open(pdf_path, "rb") as pdf_file:
                    pdf_blob = pdf_file.read()
                    pdf_id = self.pdf_service.save_pdf_to_db(pdf_blob, row.id)

                # Move and rename the PDF after the blob is saved
                new_pdf_path = self._move_pdf(pdf_path, pdf_id)

                # Update the status of the input data to 'downloaded'
                self.input_repo.update_status(row.id, "downloaded")

            except Exception as e:
                print(f"Failed to process download for record {row.id}: {e}")
                self.input_repo.update_status(row.id, "failed")

    def download_pdf(self, row, scraper: PDFSiteScraper, temp_dir: str) -> str:
        """
        Downloads the PDF for a specific record using the provided scraper.

        Args:
            row: The record containing details for downloading the PDF.
            scraper (PDFSiteScraper): The scraper to execute the web download steps.
            temp_dir (str): The temporary directory to store the downloaded PDF.

        Returns:
            str: The file path of the downloaded PDF.
        """
        return scraper.download_pdf(
            row.acct_number, row.check_number, row.amount, row.date, temp_dir
        )

    def _move_pdf(self, pdf_path: str, pdf_id: str) -> str:
        """
        Moves the downloaded PDF to the final directory with a unique name.

        Args:
            pdf_path (str): The original file path of the downloaded PDF.
            pdf_id (str): The ID of the PDF record.

        Returns:
            str: The new file path of the PDF.
        """
        download_directory = "data/stored_pdfs"
        os.makedirs(download_directory, exist_ok=True)

        unique_pdf_name = f"{pdf_id}.pdf"
        new_pdf_path = os.path.join(download_directory, unique_pdf_name)
        shutil.move(pdf_path, new_pdf_path)
        return new_pdf_path
