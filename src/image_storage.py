import sqlite3

import cv2


class ImageStorage:
    """
    A class to handle the storage of images as BLOBs in an SQLite database.

    Attributes:
        db_path (str): The file path to the SQLite database.
    """

    def __init__(self, db_path="use_cases.db"):
        """
        Initialize the ImageStorage class with the database path.

        Args:
            db_path (str): The file path to the SQLite database. Defaults to
                "use_cases.db".
        """
        self.db_path = db_path

    def save_image_blob(self, pdf_data_id, image, processing_type, ocr_text=None):
        """
        Store an image as a BLOB in the database with its associated processing
        type and optional OCR text.

        Args:
            pdf_data_id (int): The ID of the corresponding PDF data record.
            image (numpy.ndarray): The image data to be stored.
            processing_type (str): The type of image processing applied (e.g.,
                "grayscale", "binarized").
            ocr_text (str, optional): The OCR text extracted from the image,
                if any. Defaults to None.

        Returns:
            None

        Raises:
            sqlite3.DatabaseError: If there is an error during the database
                transaction.

        Example usage:
            storage = ImageStorage(db_path="use_cases.db")
            image = cv2.imread("path/to/your/image.png")
            storage.save_image_blob(1, image, "grayscale")
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Convert the image to a BLOB
        is_success, buffer = cv2.imencode(".png", image)
        image_blob = buffer.tobytes()

        # Store the image BLOB in the database with the processing type
        cursor.execute(
            """
        INSERT INTO ocr_images (pdf_data_id, processing_type, image_blob, ocr_text)
        VALUES (?, ?, ?, ?)""",
            (pdf_data_id, processing_type, image_blob, ocr_text),
        )

        conn.commit()
        conn.close()


# Example usage:
# if __name__ == "__main__":
#     db_path = "use_cases.db"
#     storage = ImageStorage(db_path=db_path)
#     # Example dummy data
#     pdf_data_id = 1
#     image = cv2.imread("path/to/your/image.png")  # Replace with actual image data
#     processing_type = "grayscale"
#     storage.save_image_blob(pdf_data_id, image, processing_type)
