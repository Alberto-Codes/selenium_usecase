from sqlalchemy import Column, Integer, String

from src.db.db_setup import Base
from src.db.utils import generate_uuid


class TblRCNBatchStatus(Base):
    """
    Represents the table for tracking the status of batch processing
    operations.

    Attributes:
        id (str): Primary key, unique identifier for each batch status.
        batch_id (str): Unique identifier for the batch.
        status (str): Status of the batch (e.g., 'pending', 'completed').
        failed_records (int): Number of records in the batch that failed to
            process.
    """

    __tablename__ = "tbl_RCN_Batch"

    id = Column(String, primary_key=True, default=generate_uuid)
    batch_id = Column(String, nullable=False, unique=True)
    status = Column(String, default="pending")
    failed_records = Column(Integer, default=0)
