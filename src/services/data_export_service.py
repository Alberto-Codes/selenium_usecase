import csv
import shutil
from pathlib import Path

from sqlalchemy.orm import Session

from src.db.repositories.input_repository import InputRepository
from src.db.repositories.ocr_result_repository import OCRResultRepository


class DataExportService:
    """
    Service class responsible for exporting data and associated files to a
    specified directory.

    Attributes:
        session (Session): SQLAlchemy session for database operations.
        target_directory (Path): Directory where data and files will be exported.
        ocr_repo (OCRResultRepository): Repository for OCR result records.
        input_repo (InputRepository): Repository for input records related to
            the OCR results.
        image_directory (Path): Directory where the original images are stored.
        images_output_dir (Path): Directory within the target directory where
            images will be copied.
    """

    def __init__(self, session: Session, target_directory: str, image_directory: str):
        """
        Initializes the DataExportService with a database session, a target
        directory, and an image directory.

        Args:
            session (Session): The SQLAlchemy session to interact with the
                database.
            target_directory (str): The path to the directory where data and
                files should be exported.
            image_directory (str): The path to the directory where images are stored.
        """
        self.session = session
        self.target_directory = Path(target_directory)
        self.image_directory = Path(image_directory)
        self.ocr_repo = OCRResultRepository(session)
        self.input_repo = InputRepository(session)
        self.target_directory.mkdir(parents=True, exist_ok=True)

        # Create a single subdirectory for all images within the target directory
        self.images_output_dir = self.target_directory / "images"
        self.images_output_dir.mkdir(parents=True, exist_ok=True)

    def export_data_with_files(self) -> None:
        """
        Exports data and associated files to the target directory.

        This method retrieves records from the OCR and Input repositories,
        copies the associated files to a single subdirectory within the target
        directory, and generates a CSV file containing data from both the
        input records and the OCR results.

        The CSV file contains the following fields:
        - input_id
        - account_number
        - check_number
        - amount
        - issue_date
        - file_name
        - ocr_text

        If a file does not exist, it logs an error message instead of copying
        the file.
        """
        records = self.ocr_repo.get_records_with_input()
        extract_file_path = self.target_directory / "extracted_data.csv"

        with extract_file_path.open(mode="w", newline="") as csvfile:
            fieldnames = [
                "input_id",
                "account_number",
                "check_number",
                "amount",
                "issue_date",
                "file_name",
                "ocr_text",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for ocr_record, input_record in records:
                # Construct the path to the image file using the image ID
                original_file_path = self.image_directory / f"{ocr_record.image_id}.png"

                if original_file_path.exists():
                    destination_path = self.images_output_dir / original_file_path.name
                    shutil.copy2(original_file_path, destination_path)

                    writer.writerow(
                        {
                            "input_id": input_record.id,
                            "account_number": input_record.account_number,
                            "check_number": input_record.check_number,
                            "amount": input_record.amount,
                            "issue_date": input_record.issue_date,
                            "file_name": original_file_path.name,
                            "ocr_text": ocr_record.extracted_text,
                        }
                    )

                    print(
                        f"Copied {original_file_path} to {destination_path} "
                        f"and wrote extract data."
                    )
                else:
                    print(
                        f"File {original_file_path} does not exist and cannot "
                        f"be copied."
                    )
