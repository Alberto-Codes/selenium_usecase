from prefect import flow, task
from sqlalchemy.orm import sessionmaker
from src.db.db_setup import get_session, TblRCNImage
from src.utils.image_saver import ImageSaver

@task
def fetch_raw_images(session):
    """
    Fetch images from the database that have the processing type 'raw' and are linked
    to input records with a status of 'converted'.
    """
    return (
        session.query(TblRCNImage)
        .join(TblRCNInput, TblRCNImage.input_table_id == TblRCNInput.id)
        .filter(TblRCNImage.processing_type == "raw", TblRCNInput.status == "converted")
        .all()
    )

@task
def save_image(image_saver: ImageSaver, image_record: TblRCNImage):
    """
    Save an image using the ImageSaver class.
    """
    image_saver.save_image(image_record)

@flow
def save_images_flow():
    """
    Prefect flow to save images with 'raw' processing type and input status 'converted',
    and update the database.
    """
    session = get_session()

    # Instantiate the ImageSaver class
    image_saver = ImageSaver(session=session)

    # Fetch raw images with input status 'converted'
    raw_images = fetch_raw_images(session).result()

    # Save each image and update the database
    for image_record in raw_images:
        save_image(image_saver, image_record)

    session.close()
