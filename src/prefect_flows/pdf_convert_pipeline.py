from prefect import flow, task
from sqlalchemy.orm import Session
from src.db.db_setup import get_session
from src.db.models import TblRCNInput, TblRCNPDF
from src.download_manager import PDFConverter, ImageStorage


@task
def fetch_downloaded_pdfs(session: Session):
    """
    Fetch records with status 'downloaded' from the TblRCNInput table.

    Args:
        session (Session): The SQLAlchemy session for database operations.

    Returns:
        list: A list of records with status 'downloaded'.
    """
    return session.query(TblRCNInput).filter(TblRCNInput.status == 'downloaded').all()


@task
def convert_and_store_images(session: Session, input_records):
    """
    Convert PDF blobs to images and store them in the TblRCNImage table.

    Args:
        session (Session): The SQLAlchemy session for database operations.
        input_records (list): List of input records to process.

    Returns:
        None
    """
    for input_record in input_records:
        # Fetch the corresponding PDF record
        pdf_record = session.query(TblRCNPDF).filter(TblRCNPDF.input_table_id == input_record.id).one_or_none()

        if pdf_record:
            # Convert the PDF to images
            pdf_converter = PDFConverter(pdf_record.pdf_blob)
            images = pdf_converter.convert_to_images()

            # Store each image in the TblRCNImage table
            image_storage = ImageStorage(session)
            for image in images:
                image_storage.save_image_blob(input_table_id=input_record.id, image=image)

            # Update the status of the input record to 'converted'
            input_record.status = 'converted'
            session.commit()


@flow
def convert_pdf_to_image_flow(db_path: str = "data/rcn.db"):
    """
    Prefect flow to handle converting PDFs to images and storing them in the database.

    Args:
        db_path (str): Path to the DuckDB database.
    """
    session = get_session(db_path=db_path)
    input_records = fetch_downloaded_pdfs(session=session)
    convert_and_store_images(session=session, input_records=input_records)


if __name__ == "__main__":
    convert_pdf_to_image_flow()
