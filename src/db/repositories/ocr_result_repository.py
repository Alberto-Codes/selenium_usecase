from typing import List, Tuple
from sqlalchemy.orm import Session
from src.db.models.ocr_result import TblRCNOCRResult
from src.db.models.input import TblRCNInput

class OCRResultRepository:
    """
    Repository for performing CRUD operations on the TblRCNOCRResult table.
    """

    def __init__(self, session: Session):
        """
        Initializes the OCRResultRepository with a SQLAlchemy session.

        Args:
            session (Session): The SQLAlchemy session for database operations.
        """
        self.session = session

    def save_ocr_result(
        self, image_id: str, extracted_text: str, preprocessing_type: str
    ) -> TblRCNOCRResult:
        """
        Saves OCR results to the database.

        Args:
            image_id (str): The ID of the image associated with the OCR result.
            extracted_text (str): The extracted OCR text.
            preprocessing_type (str): The type of preprocessing applied
                (e.g., "raw").

        Returns:
            TblRCNOCRResult: The saved OCR result record.
        """
        ocr_result = TblRCNOCRResult(
            image_id=image_id,
            preprocessing_type=preprocessing_type,
            extracted_text=extracted_text,
            payee_match="no",  # Assume 'no' initially; updated later during payee matching
        )
        self.session.add(ocr_result)
        self.session.commit()
        return ocr_result

    def get_ocr_records_for_matching(
        self, preprocessing_type: str
    ) -> List[TblRCNOCRResult]:
        """
        Retrieves OCR records for matching based on the preprocessing type.

        Args:
            preprocessing_type (str): The type of preprocessing applied to 
                filter OCR results.

        Returns:
            List[TblRCNOCRResult]: A list of OCR results that match the 
                preprocessing type.
        """
        return (
            self.session.query(TblRCNOCRResult)
            .filter_by(preprocessing_type=preprocessing_type)
            .all()
        )

    def update_payee_match(
        self, ocr_record: TblRCNOCRResult, matched: dict, 
        possible_matches: List[str]
    ) -> None:
        """
        Updates the payee match status of an OCR record.

        Args:
            ocr_record (TblRCNOCRResult): The OCR result record to update.
            matched (dict): A dictionary indicating whether matches were found.
            possible_matches (List[str]): A list of possible matches (not 
                currently used in this logic).

        Returns:
            None
        """
        ocr_record.payee_match = "yes" if any(matched.values()) else "no"
        self.session.commit()

    def get_records_with_zero_payee_match(self) -> List[TblRCNOCRResult]:
        """
        Fetches OCR records where `payee_match` is 'no'.

        Returns:
            List[TblRCNOCRResult]: A list of OCR records where `payee_match` 
                is 'no'.
        """
        return (
            self.session.query(TblRCNOCRResult)
            .filter_by(payee_match="no")
            .all()
        )

    def get_records_with_input(self) -> List[Tuple[TblRCNOCRResult, TblRCNInput]]:
        """
        Fetch OCR results where `payee_match` is 'no' and join with the input 
        records.

        Returns:
            List[Tuple[TblRCNOCRResult, TblRCNInput]]: A list of tuples 
                containing OCR results and their corresponding input records.
        """
        return (
            self.session.query(TblRCNOCRResult, TblRCNInput)
            .join(TblRCNInput, TblRCNOCRResult.image_id == TblRCNInput.id)
            .filter(TblRCNOCRResult.payee_match == "no")
            .all()
        )
