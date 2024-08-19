from sqlalchemy import Column, ForeignKey, LargeBinary, String

from src.db.db_setup import Base
from src.db.utils import generate_uuid


class TblRCNImage(Base):
    """
    Represents the table for storing images as BLOBs, linked to the input
    table and optionally to a PDF.

    Attributes:
        id (str): Primary key, unique identifier for each image.
        input_table_id (str): Foreign key linking to the input table.
        pdf_id (str): Foreign key linking to a PDF record, if the image was
            generated from a PDF.
        image_blob (LargeBinary): BLOB storage for the image file.
    """

    __tablename__ = "tbl_RCN_Image"

    id = Column(String, primary_key=True, default=generate_uuid)
    input_table_id = Column(String, ForeignKey("tbl_RCN_Input.id"), nullable=False)
    pdf_id = Column(String, ForeignKey("tbl_RCN_PDF.id"), nullable=True)
    image_blob = Column(LargeBinary, nullable=False)
