from prefect import flow, task
from sqlalchemy.orm import sessionmaker
from src.db.db_setup import get_session, TblRCNImage, TblRCNOCRResult, TblRCNInput
from src.utils.ocr_processor import OCRProcessor

@task
def fetch_images_for_ocr(session):
    """
    Fetch images that are linked to input records with a status of 'raw_image_saved'.
    """
    return (
        session.query(TblRCNImage)
        .join(TblRCNInput, TblRCNImage.input_table_id == TblRCNInput.id)
        .filter(TblRCNInput.status == "raw_image_saved")
        .all()
    )

@task
def extract_text_from_image(ocr_processor: OCRProcessor, image_record: TblRCNImage):
    """
    Extract text from an image using the OCRProcessor and save the result in the database.
    """
    # Convert BLOB back to an image object
    image = Image.open(io.BytesIO(image_record.image_blob))
    
    # Extract text using Tesseract
    extracted_text = ocr_processor.extract_text(image)

    return extracted_text

@task
def save_ocr_result(session, image_record, extracted_text):
    """
    Save the OCR result in the database.
    """
    ocr_result = TblRCNOCRResult(
        image_id=image_record.id,
        preprocessing_type="raw",  # Set preprocessing type as 'raw'
        extracted_text=extracted_text,
    )
    session.add(ocr_result)

    # Update the status of the input record to 'text_extracted'
    input_record = (
        session.query(TblRCNInput).filter_by(id=image_record.input_table_id).first()
    )
    input_record.status = "text_extracted"

    session.commit()

@flow
def ocr_extraction_flow():
    """
    Prefect flow to extract text from images and save the results in the OCR table.
    """
    session = get_session()

    # Instantiate the OCRProcessor class
    ocr_processor = OCRProcessor()

    # Fetch images linked to input records with status 'raw_image_saved'
    raw_images = fetch_images_for_ocr(session).result()

    # Process each image
    for image_record in raw_images:
        extracted_text = extract_text_from_image(ocr_processor, image_record).result()
        save_ocr_result(session, image_record, extracted_text)

    session.close()
