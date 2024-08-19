from typing import List, Optional

from sqlalchemy.orm import Session

from src.db.models.input import TblRCNInput


class InputRepository:
    """
    Repository for performing CRUD operations on the TblRCNInput table.
    """

    def __init__(self, session: Session):
        """
        Initializes the InputRepository with a SQLAlchemy session.

        Args:
            session (Session): The SQLAlchemy session for database operations.
        """
        self.session = session

    def select_records(
        self,
        status: Optional[str] = None,
        batch_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[TblRCNInput]:
        """
        Selects records based on status and/or batch ID, with an optional limit and offset.

        Args:
            status (Optional[str]): Status to filter input records.
            batch_id (Optional[str]): Batch ID to filter input records.
            limit (Optional[int]): Limit on the number of records to fetch.
            offset (Optional[int]): Number of records to skip before fetching.

        Returns:
            List[TblRCNInput]: List of input records that match the filters.
        """
        query = self.session.query(TblRCNInput)

        if status:
            query = query.filter_by(status=status)
        if batch_id:
            query = query.filter_by(batch_uuid=batch_id)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        return query.all()

    def get_records_by_batch_id(self, batch_id: str) -> List[TblRCNInput]:
        """
        Fetches input records by batch ID.

        Args:
            batch_id (str): The batch ID to filter input records.

        Returns:
            List[TblRCNInput]: List of input records for the given batch ID.
        """
        return self.select_records(batch_id=batch_id)

    def select_pending_records(self, limit: int) -> List[TblRCNInput]:
        """
        Selects records with 'pending' status.

        Args:
            limit (int): Number of records to fetch.

        Returns:
            List[TblRCNInput]: List of 'pending' input records.
        """
        return self.select_records(status="pending", limit=limit)

    def update_records_with_batch(
        self, records: List[TblRCNInput], batch_id: str
    ) -> None:
        """
        Updates the records to associate them with a batch and set their status to 'in_progress'.

        Args:
            records (List[TblRCNInput]): List of records to update.
            batch_id (str): The batch ID to associate with the records.

        Returns:
            None
        """
        for record in records:
            record.status = "in_progress"
            record.batch_uuid = batch_id
        self.session.commit()

    def update_records_status(self, record_ids: List[str], status: str) -> None:
        """
        Updates the status of input records.

        Args:
            record_ids (List[str]): List of input record IDs to update.
            status (str): The new status to set for the input records.

        Returns:
            None
        """
        self.session.query(TblRCNInput).filter(TblRCNInput.id.in_(record_ids)).update(
            {"status": status}, synchronize_session=False
        )
        self.session.commit()

    def get_input_by_id(self, input_id: str) -> Optional[TblRCNInput]:
        """
        Retrieves a specific input record by its ID.

        Args:
            input_id (str): The ID of the input record to retrieve.

        Returns:
            Optional[TblRCNInput]: The input record, or None if not found.
        """
        return self.session.query(TblRCNInput).filter_by(id=input_id).first()

    def update_status(self, input_id: str, status: str) -> None:
        """
        Updates the status of a specific input record.

        Args:
            input_id (str): The ID of the input record to update.
            status (str): The new status to set for the input record.

        Returns:
            None
        """
        self.session.query(TblRCNInput).filter_by(id=input_id).update(
            {"status": status}
        )
        self.session.commit()
