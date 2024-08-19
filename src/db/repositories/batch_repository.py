from sqlalchemy.orm import Session

from src.db.models.batch_status import TblRCNBatchStatus


class BatchRepository:
    """
    Repository for performing CRUD operations on the TblRCNBatchStatus table.
    """

    def __init__(self, session: Session):
        """
        Initializes the BatchRepository with a SQLAlchemy session.

        Args:
            session (Session): The SQLAlchemy session for database operations.
        """
        self.session = session

    def create_batch(self, batch_id: str) -> TblRCNBatchStatus:
        """
        Creates a new batch record in the database.

        Args:
            batch_id (str): The ID of the new batch.

        Returns:
            TblRCNBatchStatus: The created batch record.
        """
        new_batch = TblRCNBatchStatus(id=batch_id, status="pending", failed_records=0)
        self.session.add(new_batch)
        self.session.commit()
        return new_batch

    def update_batch_status(self, batch_id: str, status: str) -> None:
        """
        Updates the status of a batch record in the database.

        Args:
            batch_id (str): The ID of the batch to update.
            status (str): The new status to set for the batch.

        Returns:
            None
        """
        self.session.query(TblRCNBatchStatus).filter_by(id=batch_id).update(
            {"status": status}
        )
        self.session.commit()
