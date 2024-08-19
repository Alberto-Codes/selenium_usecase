from typing import Optional, List
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

    def create_pdf_record(self, input_table_id: str, pdf_blob: bytes) -> TblRCNPDF:
        """
        Creates a new PDF record in the database.

        Args:
            input_table_id (str): The ID of the related input table record.
            pdf_blob (bytes): The PDF data as a binary large object (BLOB).

        Returns:
            TblRCNPDF: The created PDF record.
        """
        pdf_record = TblRCNPDF(input_table_id=input_table_id, pdf_blob=pdf_blob)
        self.session.add(pdf_record)
        self.session.commit()
        return pdf_record

    def update_pdf_blob(self, pdf_id: str, pdf_blob: bytes) -> Optional[TblRCNPDF]:
        """
        Updates the PDF blob for a given PDF record.

        Args:
            pdf_id (str): The ID of the PDF record to update.
            pdf_blob (bytes): The new PDF data as a binary large object (BLOB).

        Returns:
            Optional[TblRCNPDF]: The updated PDF record, or None if the record was not found.
        """
        pdf_record = self.session.query(TblRCNPDF).filter_by(id=pdf_id).first()
        if pdf_record:
            pdf_record.pdf_blob = pdf_blob
            self.session.commit()
        return pdf_record

    def delete_pdf_by_id(self, pdf_id: str) -> bool:
        """
        Deletes a PDF record by its ID.

        Args:
            pdf_id (str): The ID of the PDF record to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        pdf_record = self.session.query(TblRCNPDF).filter_by(id=pdf_id).first()
        if pdf_record:
            self.session.delete(pdf_record)
            self.session.commit()
            return True
        return False

    def get_all_pdfs(self, limit: Optional[int] = None) -> List[TblRCNPDF]:
        """
        Fetches all PDF records, optionally limited by a maximum number of records.

        Args:
            limit (Optional[int]): The maximum number of records to fetch.

        Returns:
            List[TblRCNPDF]: A list of all PDF records.
        """
        query = self.session.query(TblRCNPDF)
        if limit:
            query = query.limit(limit)
        return query.all()
