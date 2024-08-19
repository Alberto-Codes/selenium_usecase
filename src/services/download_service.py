import os
import shutil

from sqlalchemy.orm import Session

from src.db.repositories.image_repository import ImageRepository
from src.db.repositories.pdf_repository import PDFRepository
from src.scrapers.pdf_site_scraper import PDFSiteScraper
from src.services.pdf_processing_service import PDFProcessingService


class DownloadService:
    """
    Service class for handling the download of PDFs, converting them to images,
    and storing them in the database.
    """

    def __init__(self, session: Session):
        """
        Initializes the DownloadService.

        Args:
            session (Session): The SQLAlchemy session for database operations.
        """
        self.pdf_repo = PDFRepository(session)
        self.image_repo = ImageRepository(session)
        self.pdf_service = PDFProcessingService()

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

    def process_rows_for_download(
        self, scraper: PDFSiteScraper, download_directory: str = "data/stored_pdfs"
    ) -> None:
        """
        Processes rows with a 'pending' status from the database. Downloads PDFs,
        converts them to images, and stores both in the database.

        Args:
            scraper (PDFSiteScraper): Scraper to execute the web download steps.
            download_directory (str): Directory to store downloaded PDFs. Defaults to "data/stored_pdfs".

        Returns:
            None
        """
        os.makedirs(download_directory, exist_ok=True)

        # Fetch pending rows from the database
        pending_rows = self.pdf_repo.get_pending_rows()

        for row in pending_rows:
            try:
                # Download the PDF
                pdf_path = self.download_pdf(row, scraper)
                new_pdf_path = self._move_pdf(pdf_path, row, download_directory)

                # Store the PDF as a BLOB in the database
                pdf_blob = self.pdf_service.load_pdf_as_blob(new_pdf_path)
                pdf_id = self.pdf_repo.save_pdf_blob(row.id, pdf_blob, new_pdf_path)

                # Convert the PDF BLOB to images
                images = self.pdf_service.convert_pdf_to_images(pdf_blob)

                # Store the images as BLOBs in the database
                for image in images:
                    self.image_repo.save_image_blob(row.id, pdf_id, image)

                # Update the status of the input data to 'downloaded'
                self.pdf_repo.update_row_status(row.id, "downloaded")

            except Exception as e:
                print(f"Failed to download for row {row.id}: {e}")
                self.pdf_repo.update_row_status(row.id, "failed")

    def _move_pdf(self, pdf_path: str, row, download_directory: str) -> str:
        """
        Moves the downloaded PDF to the target directory with a unique name.

        Args:
            pdf_path (str): The original file path of the downloaded PDF.
            row (Row): The row data to generate a unique file name.
            download_directory (str): The directory to move the PDF to.

        Returns:
            str: The new file path of the PDF.
        """
        unique_pdf_name = f"{row.uuid}.pdf"
        new_pdf_path = os.path.join(download_directory, unique_pdf_name)
        shutil.move(pdf_path, new_pdf_path)
        return new_pdf_path
