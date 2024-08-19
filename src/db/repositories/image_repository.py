from sqlalchemy.orm import Session

from src.db.models.image import TblRCNImage


class ImageRepository:
    """
    Repository for performing CRUD operations on the TblRCNImage table.
    """

    def __init__(self, session: Session):
        """
        Initializes the ImageRepository with the given session.

        Args:
            session (Session): The SQLAlchemy session for database operations.
        """
        self.session = session

    def create_image_record(
        self, pdf_id: str, input_table_id: str, image_blob: bytes, processing_type: str
    ) -> TblRCNImage:
        """
        Creates a new image record in the database.

        Args:
            input_table_id (str): The ID of the corresponding TblRCNInput record.
            image_blob (bytes): The image data to be stored as a BLOB.
            processing_type (str): The type of image processing applied.

        Returns:
            TblRCNImage: The created image record.
        """
        image_record = TblRCNImage(
            input_table_id=input_table_id,
            pdf_id=pdf_id,
            image_blob=image_blob,
            processing_type=processing_type,
        )
        self.session.add(image_record)
        self.session.commit()
        return image_record
