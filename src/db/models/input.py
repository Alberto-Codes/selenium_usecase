from sqlalchemy import Column, Date, Float, ForeignKey, String

from src.db.db_setup import Base
from src.db.utils import generate_uuid


class TblRCNInput(Base):
    """
    Represents the input table for records, tracking basic details like account
    number, check number, amount, payee, and status.

    Attributes:
        id (str): Primary key, unique identifier for each record.
        guid (str): Unique GUID for each record.
        account_number (str): Account number associated with the record.
        check_number (str): Check number associated with the record.
        amount (float): Amount associated with the record.
        payee (str): Payee associated with the record.
        issue_date (Date): Date the check was issued.
        batch_uuid (str): Foreign key linking to a batch record.
        status (str): Status of the record (e.g., 'pending', 'processed').
    """

    __tablename__ = "tbl_RCN_Input"

    id = Column(String, primary_key=True, default=generate_uuid)
    guid = Column(String, unique=True, nullable=False)
    account_number = Column(String)
    check_number = Column(String)
    amount = Column(Float)
    payee = Column(String)
    issue_date = Column(Date)
    batch_uuid = Column(String, ForeignKey("tbl_RCN_Batch.id"), nullable=True)
    status = Column(String, default="pending")
