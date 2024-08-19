from typing import List, Tuple

from prefect import flow, task

from src.db.db_connect import session
from src.db.repositories.input_repository import InputRepository
from src.db.repositories.ocr_result_repository import OCRResultRepository
from src.db.repositories.pdf_repository import PDFRepository
from src.services.ocr_extraction_service import OCRExtractionService
from src.services.pdf_processing_service import PDFImageProcessingService


@task
def fetch_input_records(batch_id: str):
    """
    Fetch input records by batch ID.

    Args:
        batch_id (str): The batch ID to filter input records.

    Returns:
        List[InputRecord]: List of input records associated with the batch ID.
    """
    input_repo = InputRepository(session)
    return input_repo.get_records_by_batch_id(batch_id)


@task
def process_pdf_to_images(pdf_blob: bytes, input_table_id: str, pdf_id: str):
    """
    Convert a PDF blob to images and save them to disk.

    Args:
        pdf_blob (bytes): The PDF data as a binary large object (BLOB).
        input_table_id (str): The ID of the related input record.
        pdf_id (str): The ID of the PDF record.

    Returns:
        List[Tuple[str, str, bytes]]: A list of tuples containing image paths,
        image IDs, and image blobs.
    """
    pdf_image_service = PDFImageProcessingService()
    return pdf_image_service.convert_pdf_to_images(
        pdf_blob, input_table_id, pdf_id, save_to_disk=True, save_blob_to_db=False
    )


@task
def extract_ocr_from_images(image_paths: List[Tuple[str, str, bytes]]):
    """
    Extract OCR text from images and save the results to the database.

    Args:
        image_paths (List[Tuple[str, str, bytes]]): List of image paths, IDs,
        and image blobs.
    """
    ocr_service = OCRExtractionService(session)
    for image_path, image_id, image_blob in image_paths:
        ocr_service.extract_and_save_ocr_results(image_blob, image_id)


@flow
def batch_processing_flow(batch_id: str):
    """
    Main flow to process a batch of input records by converting PDFs to images
    and extracting OCR text.

    Args:
        batch_id (str): The batch ID to process.
    """
    input_records = fetch_input_records(batch_id)
    pdf_repo = PDFRepository(session)

    for record in input_records:
        pdf_record = pdf_repo.get_pdf_by_input_id(record.id)
        image_paths = process_pdf_to_images(
            pdf_record.pdf_blob, record.id, pdf_record.id
        )
        extract_ocr_from_images(image_paths)

    # Update the input records' status to reflect that processing is complete
    input_repo = InputRepository(session)
    input_repo.update_records_status(
        [record.id for record in input_records], "processed"
    )


# Example invocation
if __name__ == "__main__":
    batch_processing_flow(batch_id="your_batch_id_here")
