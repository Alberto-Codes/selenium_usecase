"""
This module initializes the SQLAlchemy declarative base and imports all
model classes to ensure they are registered properly with the ORM.
"""

from sqlalchemy.ext.declarative import declarative_base

from .batch_status import TblRCNBatchStatus
from .image import TblRCNImage
from .input import TblRCNInput
from .ocr_result import TblRCNOCRResult
from .pdf import TblRCNPDF

__all__ = [
    "Base",
    "TblRCNImage",
    "TblRCNInput",
    "TblRCNPDF",
    "TblRCNOCRResult",
    "TblRCNBatchStatus",
]


Base = declarative_base()
