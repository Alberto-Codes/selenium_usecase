from sqlalchemy import Column, ForeignKey, LargeBinary, String

from src.db.db_setup import Base
from src.db.utils import generate_uuid


class TblRCNPDF(Base):
    """
    Represents the table for storing PDF files as BLOBs linked to the input
    table.

    Attributes:
        id (str): Primary key, unique identifier for each PDF.
        input_table_id (str): Foreign key linking to the input table.
        pdf_blob (LargeBinary): BLOB storage for the PDF file.
    """

    __tablename__ = "tbl_RCN_PDF"

    id = Column(String, primary_key=True, default=generate_uuid)
    input_table_id = Column(String, ForeignKey("tbl_RCN_Input.id"), nullable=False)
    pdf_blob = Column(LargeBinary, nullable=False)
