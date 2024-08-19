from typing import Optional

from sqlalchemy.orm import Session

from src.db.models.pdf import TblRCNPDF


class PDFRepository:
    """
    Repository for performing CRUD operations on the TblRCNPDF table.
    """

    def __init__(self, session: Session):
        """
        Initializes the PDFRepository with a SQLAlchemy session.

        Args:
            session (Session): The SQLAlchemy session for database operations.
        """
        self.session = session

    def get_pdf_by_input_id(self, input_table_id: str) -> Optional[TblRCNPDF]:
        """
        Fetches the PDF record related to the given input table ID.

        Args:
            input_table_id (str): The ID of the input table record.

        Returns:
            Optional[TblRCNPDF]: The PDF record associated with the input table
            ID, or None if no record is found.
        """
        return (
            self.session.query(TblRCNPDF)
            .filter_by(input_table_id=input_table_id)
            .first()
        )
