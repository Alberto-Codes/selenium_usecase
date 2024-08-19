from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

from src.db.repositories.input_repository import InputRepository
from src.db.repositories.ocr_result_repository import OCRResultRepository
from src.utils.payee_matcher import PayeeMatcher


class PayeeMatchingService:
    """
    Service class for handling the payee matching process, including fetching
    OCR records, performing payee matching, and updating the results in the database.
    """

    def __init__(self, session: Session):
        """
        Initializes the PayeeMatchingService with a SQLAlchemy session.

        Args:
            session (Session): The SQLAlchemy session for database operations.
        """
        self.session = session
        self.ocr_repo = OCRResultRepository(session)
        self.input_repo = InputRepository(session)
        self.matcher = PayeeMatcher()

    def fetch_ocr_records(self) -> List:
        """
        Fetches OCR records that are ready for payee matching.

        Returns:
            List: A list of OCR records to be matched.
        """
        return self.ocr_repo.get_ocr_records_for_matching(preprocessing_type="raw")

    def match_and_update_payees(self, ocr_record) -> Tuple[Dict[str, bool], List[str]]:
        """
        Matches payees against OCR-extracted text and updates the database with the results.

        Args:
            ocr_record: The OCR record containing extracted text to match against payees.

        Returns:
            Tuple[Dict[str, bool], List[str]]: A tuple containing the match results and possible matches.
        """
        input_record = self.input_repo.get_input_by_id(ocr_record.image.input_table_id)
        payees = [input_record.payee_1, input_record.payee_2]

        matched, possible_matches = self.matcher.match_payees(
            ocr_record.extracted_text, payees
        )

        self.ocr_repo.update_payee_match(ocr_record, matched, possible_matches)
        self.input_repo.update_status(input_record.id, "payee_match_attempted")

        return matched, possible_matches
