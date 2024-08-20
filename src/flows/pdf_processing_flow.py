from typing import List, Tuple

from prefect import flow, task

from src.db.db_connect import engine, get_session
from src.db.repositories.input_repository import InputRepository
from src.db.repositories.pdf_repository import PDFRepository
from src.services.ocr_extraction_service import OCRExtractionService
from src.services.pdf_processing_service import PDFProcessingService
from src.services.payee_matching_service import PayeeMatchingService


@task
def fetch_input_records(session, batch_id: str) -> List:
    """
    Fetches input records associated with a specific batch ID.

    Args:
        session (Session): The SQLAlchemy session for database operations.
        batch_id (str): The batch ID to filter input records.

    Returns:
        List[InputRecord]: A list of input records linked to the batch ID.
    """
    input_repo = InputRepository(session)
    return input_repo.get_records_by_batch_id(batch_id)


@task
def process_pdf_to_images(session, pdf_blob: bytes, input_table_id: str, 
                          pdf_id: str) -> List[Tuple[str, str, bytes]]:
    """
    Converts a PDF blob into images and saves them to disk.

    Args:
        session (Session): The SQLAlchemy session for database operations.
        pdf_blob (bytes): The PDF data as a binary large object (BLOB).
        input_table_id (str): The ID of the related input record.
        pdf_id (str): The ID of the PDF record.

    Returns:
        List[Tuple[str, str, bytes]]: A list of tuples, each containing the 
        image path, image ID, and image blob.
    """
    pdf_service = PDFProcessingService()
    return pdf_service.convert_pdf_to_images(
        pdf_blob, input_table_id, pdf_id, save_to_disk=True, 
        save_blob_to_db=False
    )


@task
def extract_ocr_from_images(session, 
                            image_paths: List[Tuple[str, str, bytes]]):
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
def match_payees(session):
    """
    Performs payee matching on OCR records and updates the database with 
    results.

    Args:
        session (Session): The SQLAlchemy session for database operations.
    """
    payee_service = PayeeMatchingService(session)
    ocr_records = payee_service.fetch_ocr_records()

    for ocr_record in ocr_records:
        payee_service.match_and_update_payees(ocr_record)


@flow
def pdf_processing_flow(batch_id: str):
    """
    Main flow to process a batch of input records by converting PDFs to images,
    extracting OCR text, and matching payees.

    Args:
        batch_id (str): The batch ID to process.
    """
    session = get_session(engine)
    
    try:
        # Fetch input records by batch ID
        input_records = fetch_input_records(session, batch_id).result()

        pdf_repo = PDFRepository(session)
        input_repo = InputRepository(session)

        for record in input_records:
            pdf_record = pdf_repo.get_pdf_by_input_id(record.id)

            if pdf_record and pdf_record.pdf_blob:
                image_paths = process_pdf_to_images(
                    session, pdf_record.pdf_blob, record.id, pdf_record.id
                ).result()

                if image_paths:
                    extract_ocr_from_images(session, image_paths).result()

            else:
                print(f"Skipping record {record.id}: No PDF or empty PDF blob found.")

        # Perform payee matching after OCR extraction
        match_payees(session).result()

        # Update the input records' status to reflect that processing is complete
        input_repo.update_records_status(
            [record.id for record in input_records if pdf_record and 
            pdf_record.pdf_blob], "processed"
        )

    finally:
        session.close()


# Example invocation
if __name__ == "__main__":
    pdf_processing_flow(batch_id="your_batch_id_here")
