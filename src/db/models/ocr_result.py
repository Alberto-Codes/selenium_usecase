from sqlalchemy import Column, ForeignKey, String

from src.db.db_setup import Base
from src.db.utils import generate_uuid


class TblRCNOCRResult(Base):
    """
    Represents the table for storing OCR results, linked to images.

    Attributes:
        id (str): Primary key, unique identifier for each OCR result.
        image_id (str): Foreign key linking to the image table.
        preprocessing_type (str): The type of preprocessing applied before OCR.
        extracted_text (str): The text extracted from the image.
        payee_match (str): Indicator of whether the extracted text matches
            the expected payee.
    """

    __tablename__ = "tbl_RCN_OCR"

    id = Column(String, primary_key=True, default=generate_uuid)
    image_id = Column(String, ForeignKey("tbl_RCN_Image.id"), nullable=False)
    preprocessing_type = Column(String, nullable=True)
    extracted_text = Column(String, nullable=True)
    payee_match = Column(String, nullable=True)
