from io import BytesIO

import pytesseract
from PIL import Image
from sqlalchemy.orm import Session

from src.db.repositories.ocr_result_repository import OCRResultRepository


class OCRExtractionService:
    """
    Service class to handle OCR extraction from images and save the results
    in the database.
    """

    def __init__(self, session: Session):
        """
        Initializes the OCRExtractionService with a database session.

        Args:
            session (Session): The SQLAlchemy session for database operations.
        """
        self.ocr_repo = OCRResultRepository(session)

    def extract_and_save_ocr_results(self, image_blob: bytes, image_id: str) -> None:
        """
        Extracts text from an image blob using OCR and saves the results
        to the database.

        Args:
            image_blob (bytes): The image data in binary large object (BLOB) format.
            image_id (str): The ID of the image record in the database.

        Returns:
            None
        """
        image = Image.open(BytesIO(image_blob))
        extracted_text = pytesseract.image_to_string(image)

        # Save the OCR results to the database
        self.ocr_repo.save_ocr_result(
            image_id=image_id, extracted_text=extracted_text, preprocessing_type="raw"
        )
