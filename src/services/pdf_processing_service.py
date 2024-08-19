from io import BytesIO
from pathlib import Path
from typing import List, Optional, Tuple

from pdf2image import convert_from_bytes
from PIL import Image

from src.db.db_connect import session
from src.db.repositories.image_repository import ImageRepository
from src.db.repositories.pdf_repository import PDFRepository


class PDFProcessingService:
    """
    Service for handling PDF processing tasks, including saving PDFs to the database,
    converting PDFs to images, and managing those images in the database.
    """

    def __init__(self, output_dir: str = "data/images"):
        """
        Initializes the PDFProcessingService.

        Args:
            output_dir (str): Directory where images will be saved if
                `save_to_disk` is True. Defaults to "data/images".
        """
        self.image_repo = ImageRepository(session)
        self.pdf_repo = PDFRepository(session)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_pdf_to_db(self, pdf_blob: bytes, input_table_id: str) -> str:
        """
        Saves a PDF blob to the database.

        Args:
            pdf_blob (bytes): The PDF data as a binary large object (BLOB).
            input_table_id (str): The related input table ID.

        Returns:
            str: The ID of the saved PDF record.
        """
        pdf_record = self.pdf_repo.create_pdf_record(
            input_table_id=input_table_id, pdf_blob=pdf_blob
        )
        return pdf_record.id

    def convert_pdf_to_images(
        self,
        pdf_blob: bytes,
        input_table_id: str,
        pdf_id: str,
        save_to_disk: bool = False,
        save_blob_to_db: bool = False,
    ) -> List[Tuple[Optional[str], str, bytes]]:
        """
        Converts a PDF blob to images and logs details in the database.

        Args:
            pdf_blob (bytes): The PDF data as a binary large object (BLOB).
            input_table_id (str): The related input table ID.
            pdf_id (str): The related PDF ID.
            save_to_disk (bool): Whether to save the images to disk.
                Defaults to False.
            save_blob_to_db (bool): Whether to save the image blobs to
                the database. Defaults to False.

        Returns:
            List[Tuple[Optional[str], str, bytes]]: A list of tuples containing
            image paths, image IDs, and image blobs. If `save_to_disk` is False,
            the paths will be None.
        """
        images = convert_from_bytes(pdf_blob)
        return [
            self._process_image(
                image, input_table_id, pdf_id, save_to_disk, save_blob_to_db
            )
            for image in images
        ]

    def _process_image(
        self,
        image: Image.Image,
        input_table_id: str,
        pdf_id: str,
        save_to_disk: bool,
        save_blob_to_db: bool,
    ) -> Tuple[Optional[str], str, bytes]:
        """
        Processes an individual image by saving it to disk and/or the database.

        Args:
            image (Image.Image): The image to process.
            input_table_id (str): The related input table ID.
            pdf_id (str): The related PDF ID.
            save_to_disk (bool): Whether to save the image to disk.
            save_blob_to_db (bool): Whether to save the image blob to
                the database.

        Returns:
            Tuple[Optional[str], str, bytes]: A tuple containing the image path,
            image ID, and image blob. If `save_to_disk` is False, the path will
            be None.
        """
        image_blob = self._get_image_blob(image)
        image_record = self.image_repo.create_image_record(
            input_table_id=input_table_id,
            pdf_id=pdf_id,
            image_blob=image_blob if save_blob_to_db else None,
        )
        image_path = (
            self._save_image_to_disk(image, image_record.id) if save_to_disk else None
        )
        return image_path, image_record.id, image_blob

    @staticmethod
    def _get_image_blob(image: Image.Image) -> bytes:
        """
        Converts an image to a binary large object (BLOB).

        Args:
            image (Image.Image): The image to convert.

        Returns:
            bytes: The image as a BLOB.
        """
        with BytesIO() as img_byte_arr:
            image.save(img_byte_arr, format="JPEG")
            return img_byte_arr.getvalue()

    def _save_image_to_disk(self, image: Image.Image, image_id: str) -> str:
        """
        Saves an image to disk.

        Args:
            image (Image.Image): The image to save.
            image_id (str): The image ID for naming the file.

        Returns:
            str: The path where the image was saved.
        """
        image_path = self.output_dir / f"{image_id}.jpg"
        image.save(image_path)
        return str(image_path)
