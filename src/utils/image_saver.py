import os
from sqlalchemy.orm import Session
from src.db.db_setup import TblRCNImage, TblRCNInput

class ImageSaver:
    def __init__(self, session: Session, image_directory: str = "data/images"):
        self.session = session
        self.image_directory = image_directory

        # Ensure the image directory exists
        if not os.path.exists(self.image_directory):
            os.makedirs(self.image_directory)

    def save_image(self, image_record: TblRCNImage):
        """
        Save a single image record to the file system and update its status.

        Args:
            image_record (TblRCNImage): The image record to be saved.
        """
        image_path = os.path.join(self.image_directory, f"{image_record.id}.png")

        # Save the image blob to a file
        with open(image_path, "wb") as img_file:
            img_file.write(image_record.image_blob)

        # Update the image record's processing type
        image_record.processing_type = "saved"
        self.session.add(image_record)

        # Update the corresponding input record's status
        input_record = self.session.query(TblRCNInput).filter_by(id=image_record.input_table_id).first()
        if input_record:
            input_record.status = "raw_image_saved"
            self.session.add(input_record)

        self.session.commit()
