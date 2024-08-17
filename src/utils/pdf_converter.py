from pdf2image import convert_from_bytes
from sqlalchemy.orm import Session
from src.db.models import TblRCNPDF, TblRCNImage


class PDFConverter:
    """
    A class to handle the conversion of a PDF stored as a BLOB to images.

    Attributes:
        pdf_blob (bytes): The PDF data stored as a binary large object (BLOB).
    """

    def __init__(self, pdf_blob: bytes):
        """
        Initialize the PDFConverter with the PDF BLOB.

        Args:
            pdf_blob (bytes): The PDF data stored as a BLOB.
        """
        self.pdf_blob = pdf_blob

    def convert_to_images(self):
        """
        Convert the PDF BLOB to images.

        This method converts the PDF BLOB into a list of images, where each
        page of the PDF is represented as an image.

        Returns:
            list: A list of images corresponding to the pages of the PDF.
        """
        images = convert_from_bytes(self.pdf_blob)
        return images

