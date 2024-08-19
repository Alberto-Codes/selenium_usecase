import os
import shutil

from sqlalchemy.orm import Session

from src.db.repositories.pdf_repository import PDFRepository
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
        self.pdf_service = PDFProcessingService()

    def process_row_for_download(
        self, row, scraper: PDFSiteScraper, download_directory: str = "data/stored_pdfs"
    ) -> None:
        """
        Processes a single row: downloads a PDF, saves it to the database,
        and moves/renames the file using the generated PDF ID.

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

            # Store the PDF as a BLOB in the database and get the generated PDF ID
            pdf_blob = self.pdf_service.load_pdf_as_blob(pdf_path)
            pdf_id = self.pdf_repo.save_pdf_blob(row.id, pdf_blob, pdf_path)

            # Move and rename the PDF using the generated PDF ID
            new_pdf_path = self._move_pdf(pdf_path, pdf_id, download_directory)

            # Update the status of the input data to 'downloaded'
            self.pdf_repo.update_row_status(row.id, "downloaded")

        except Exception as e:
            print(f"Failed to process download for record {row.id}: {e}")
            self.pdf_repo.update_row_status(row.id, "failed")

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

    def _move_pdf(self, pdf_path: str, pdf_id: str, download_directory: str) -> str:
        """
        Moves the downloaded PDF to the target directory with a unique name based on the PDF ID.

        Args:
            pdf_path (str): The original file path of the downloaded PDF.
            pdf_id (str): The unique ID generated for the PDF in the database.
            download_directory (str): The directory to move the PDF to.

        Returns:
            str: The new file path of the PDF.
        """
        unique_pdf_name = f"{pdf_id}.pdf"
        new_pdf_path = os.path.join(download_directory, unique_pdf_name)
        shutil.move(pdf_path, new_pdf_path)
        return new_pdf_path
