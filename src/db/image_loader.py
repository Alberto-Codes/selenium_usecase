
import cv2
import numpy as np


class ImageStorage:
    """
    A class to handle the storage of images as BLOBs in a DuckDB database using SQLAlchemy ORM.

    Attributes:
        session (Session): The SQLAlchemy session for database operations.
    """

    def __init__(self, session: Session):
        """
        Initialize the ImageStorage class with the database session.

        Args:
            session (Session): The SQLAlchemy session for database operations.
        """
        self.session = session

    def save_image_blob(self, input_table_id: str, image: np.ndarray, processing_type: str = "processed"):
        """
        Store an image as a BLOB in the TblRCNImage table with its associated processing type.

        Args:
            input_table_id (str): The ID of the corresponding TblRCNInput record.
            image (numpy.ndarray): The image data to be stored.
            processing_type (str, optional): The type of image processing applied. Defaults to "processed".

        Returns:
            None
        """
        # Convert the image to a BLOB
        is_success, buffer = cv2.imencode(".png", image)
        image_blob = buffer.tobytes()

        # Store the image BLOB in the database
        image_record = TblRCNImage(input_table_id=input_table_id, image_blob=image_blob)
        self.session.add(image_record)
        self.session.commit()
