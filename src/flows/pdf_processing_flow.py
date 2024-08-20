from typing import List, Tuple

from prefect import flow, task

from src.db.db_connect import engine, get_session
from src.db.repositories.input_repository import InputRepository
from src.db.repositories.pdf_repository import PDFRepository
from src.services.ocr_extraction_service import OCRExtractionService
from src.services.pdf_processing_service import PDFProcessingService
from src.services.payee_matching_service import PayeeMatchingService


@task
def fetch_valid_input_records(session, batch_id: str) -> List:
    """
    Fetches input records associated with a specific batch ID that have valid 
    PDFs.

    Args:
        session (Session): The SQLAlchemy session for database operations.
        batch_id (str): The batch ID to filter input records.

    Returns:
        List[InputRecord]: A list of input records linked to the batch ID that 
        have valid PDFs.
    """
    input_repo = InputRepository(session)
    pdf_repo = PDFRepository(session)

    input_records = input_repo.get_records_by_batch_id(batch_id)
    valid_records = [
        record for record in input_records 
        if (pdf := pdf_repo.get_pdf_by_input_id(record.id)) and pdf.pdf_blob
    ]
    
    return valid_records


@task
def process_pdfs_to_images(session, 
                           input_records: List) -> List[Tuple[str, str, bytes]]:
    """
    Converts PDFs to images for each input record and saves them to disk.

    Args:
        session (Session): The SQLAlchemy session for database operations.
        input_records (List): List of valid input records with PDFs.

    Returns:
        List[Tuple[str, str, bytes]]: A list of tuples containing the image 
        path, image ID, and image blob.
    """
    pdf_service = PDFProcessingService()
    image_paths = []

    for record in input_records:
        pdf_repo = PDFRepository(session)
        pdf_record = pdf_repo.get_pdf_by_input_id(record.id)

        images = pdf_service.convert_pdf_to_images(
            pdf_blob=pdf_record.pdf_blob, 
            input_table_id=record.id, 
            pdf_id=pdf_record.id, 
            save_to_disk=True, 
            save_blob_to_db=False
        )
        image_paths.extend(images)
    
    return image_paths


@task
def extract_ocr_text_from_images(session, 
                                 image_paths: List[Tuple[str, str, bytes]]) -> None:
    """
    Extracts OCR text from images and saves the results to the database.

    Args:
        session (Session): The SQLAlchemy session for database operations.
        image_paths (List[Tuple[str, str, bytes]]): A list of tuples, each 
        containing the image path, image ID, and image blob.
    """
    ocr_service = OCRExtractionService(session)
    
    for image_path, image_id, image_blob in image_paths:
        ocr_service.extract_and_save_ocr_results(image_blob, image_id)


@task
def perform_payee_matching(session, input_records: List) -> None:
    """
    Performs payee matching on OCR records for the given input records and 
    updates the database with the results.

    Args:
        session (Session): The SQLAlchemy session for database operations.
        input_records (List): The list of input records processed in this 
        batch.
    """
    payee_service = PayeeMatchingService(session)
    
    for record in input_records:
        ocr_records = payee_service.fetch_ocr_records_by_image_id(record.id)
        
        for ocr_record in ocr_records:
            payee_service.match_and_update_payees(ocr_record)


@flow
def process_pdf_batch(batch_id: str):
    """
    Main flow to process a batch of input records by converting PDFs to images, 
    extracting OCR text, and matching payees.

    Args:
        batch_id (str): The batch ID to process.
    """
    session = get_session(engine)
    
    try:
        # Fetch input records by batch ID that have valid PDFs
        valid_input_records = fetch_valid_input_records(session, batch_id)
        
        if not valid_input_records:
            print(f"No valid PDFs found for batch {batch_id}.")
            return

        # Convert PDFs to images
        image_paths = process_pdfs_to_images(session, valid_input_records)

        if image_paths:
            # Extract OCR text from images
            extract_ocr_text_from_images(session, image_paths)

            # Perform payee matching after OCR extraction
            perform_payee_matching(session, valid_input_records)

            # Update the input records' status to reflect that processing is 
            # complete
            input_repo = InputRepository(session)
            input_repo.update_records_status(
                [record.id for record in valid_input_records], "processed"
            )

    finally:
        session.close()


# Example invocation
if __name__ == "__main__":
    process_pdf_batch(batch_id="your_batch_id_here")
