import os
import shutil

from sqlalchemy.orm import Session

from src.db.repositories.pdf_repository import PDFRepository
from src.db.repositories.input_repository import InputRepository
from src.scrapers.pdf_site_scraper import PDFSiteScraper
from src.services.pdf_processing_service import PDFProcessingService


class DownloadService:
    """
    Service class for handling the download of PDFs and storing them in the database.
    """

    def __init__(self, session: Session):
        """
        Initializes the DownloadService.

        Args:
            session (Session): The SQLAlchemy session for database operations.
        """
        self.pdf_repo = PDFRepository(session)
        self.input_repo = InputRepository(session)
        self.pdf_service = PDFProcessingService()

    def process_row_for_download(
        self, row, scraper: PDFSiteScraper, download_directory: str = "data/stored_pdfs"
    ) -> None:
        """
        Processes a single row: downloads a PDF, moves/renames it, and stores it in the database.

        Args:
            row: The record containing details for downloading the PDF.
            scraper (PDFSiteScraper): Scraper to execute the web download steps.
            download_directory (str): Directory to store downloaded PDFs. 
                Defaults to "data/stored_pdfs".

        Returns:
            None
        """
        os.makedirs(download_directory, exist_ok=True)

        try:
            # Download the PDF
            pdf_path = self.download_pdf(row, scraper)
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"No PDF file was found for record {row.id}")

            # Move and rename the PDF
            new_pdf_path = self._move_pdf(pdf_path, row, download_directory)

            # Store the PDF as a BLOB in the database
            pdf_blob = self.pdf_service.load_pdf_as_blob(new_pdf_path)
            self.pdf_repo.save_pdf_blob(row.id, pdf_blob, new_pdf_path)

            # Update the status of the input data to 'downloaded'
            self.input_repo.update_status(row.id, "downloaded")

        except Exception as e:
            print(f"Failed to process download for record {row.id}: {e}")
            # Update the status of the input data to 'failed'
            self.input_repo.update_status(row.id, "failed")

    def download_pdf(self, row, scraper: PDFSiteScraper) -> str:
        """
        Downloads the PDF for a specific record using the provided scraper.

        Args:
            row: The record containing details for downloading the PDF.
            scraper (PDFSiteScraper): Scraper to execute the web download steps.

        Returns:
            str: The file path of the downloaded PDF.
        """
        return scraper.download_pdf(
            row.acct_number, row.check_number, row.amount, row.date
        )

    def _move_pdf(self, pdf_path: str, row, download_directory: str) -> str:
        """
        Moves the downloaded PDF to the target directory with a unique name.

        Args:
            pdf_path (str): The original file path of the downloaded PDF.
            row: The row data to generate a unique file name.
            download_directory (str): The directory to move the PDF to.

        Returns:
            str: The new file path of the PDF.
        """
        unique_pdf_name = f"{row.uuid}.pdf"
        new_pdf_path = os.path.join(download_directory, unique_pdf_name)
        shutil.move(pdf_path, new_pdf_path)
        return new_pdf_path
