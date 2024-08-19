from typing import List, Tuple

from sqlalchemy.orm import Session

from src.db.repositories.batch_repository import BatchRepository
from src.db.repositories.input_repository import InputRepository
from src.db.utils.generate_uuid import generate_uuid


class BatchService:
    """
    Service class for handling batch creation and processing.
    """

    def __init__(self, session: Session):
        """
        Initializes the BatchService with the provided database session.

        Args:
            session (Session): The SQLAlchemy session for database operations.
        """
        self.batch_repo = BatchRepository(session)
        self.input_repo = InputRepository(session)

    def create_and_process_batch(self, limit: int) -> Tuple[str, List]:
        """
        Creates a new batch, updates its status, and assigns pending records
        to the batch.

        Args:
            limit (int): The maximum number of pending records to process.

        Returns:
            Tuple[str, List]: The batch ID and the list of processed records.
        """
        batch_id = generate_uuid()
        self.batch_repo.create_batch(batch_id)
        self.batch_repo.update_batch_status(batch_id, "in_progress")

        # Fetch pending records and associate them with the batch
        records = self.input_repo.select_pending_records(limit=limit)
        self.input_repo.update_records_with_batch(records, batch_id)

        return batch_id, records

    def complete_batch(self, batch_id: str) -> None:
        """
        Marks a batch as completed.

        Args:
            batch_id (str): The ID of the batch to complete.

        Returns:
            None
        """
        self.batch_repo.update_batch_status(batch_id, "completed")
