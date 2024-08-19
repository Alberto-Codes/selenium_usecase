import shutil
import csv
from pathlib import Path
from sqlalchemy.orm import Session
from src.db.repositories.ocr_result_repository import OCRResultRepository
from src.db.repositories.input_repository import InputRepository

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
    """

    def __init__(self, session: Session, target_directory: str):
        """
        Initializes the DataExportService with a database session and a target 
        directory.

        Args:
            session (Session): The SQLAlchemy session to interact with the 
                database.
            target_directory (str): The path to the directory where data and 
                files should be exported.
        """
        self.session = session
        self.target_directory = Path(target_directory)
        self.ocr_repo = OCRResultRepository(session)
        self.input_repo = InputRepository(session)
        self.target_directory.mkdir(parents=True, exist_ok=True)

    def export_data_with_files(self) -> None:
        """
        Exports data and associated files to the target directory.

        This method retrieves records from the OCR and Input repositories 
        where `payee_match` is 'no', copies the associated files to a 
        subdirectory within the target directory, and generates a CSV file 
        containing data from both the input records and the OCR results.

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
        records = self.ocr_repo.get_records_with_input(payee_match="no")
        extract_file_path = self.target_directory / "extracted_data.csv"

        with extract_file_path.open(mode="w", newline='') as csvfile:
            fieldnames = [
                "input_id", "account_number", "check_number", "amount", 
                "issue_date", "file_name", "ocr_text"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for ocr_record, input_record in records:
                original_file_path = Path(ocr_record.image.file_path)
                if original_file_path.exists():
                    sub_dir = self.target_directory / original_file_path.stem
                    sub_dir.mkdir(parents=True, exist_ok=True)

                    destination_path = sub_dir / original_file_path.name
                    shutil.copy2(original_file_path, destination_path)

                    writer.writerow({
                        "input_id": input_record.id,
                        "account_number": input_record.account_number,
                        "check_number": input_record.check_number,
                        "amount": input_record.amount,
                        "issue_date": input_record.issue_date,
                        "file_name": original_file_path.name,
                        "ocr_text": ocr_record.extracted_text
                    })

                    print(f"Copied {original_file_path} to {destination_path} "
                          f"and wrote extract data.")
                else:
                    print(f"File {original_file_path} does not exist and cannot "
                          f"be copied.")
