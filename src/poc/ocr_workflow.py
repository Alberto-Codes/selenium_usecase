import numpy as np
from image_processor import ImageProcessor
from image_storage import ImageStorage
from ocr_text_extractor import OCRTextExtractor
from pdf_converter import PDFConverter


def process_and_store_image(pdf_blob, pdf_data_id):
    """
    Process a PDF BLOB by converting it to images, applying various image
    preprocessing techniques, and storing both the processed images and the
    extracted OCR text in a database.

    Args:
        pdf_blob (bytes): The BLOB data of the PDF to be processed.
        pdf_data_id (int): The ID of the corresponding record in the `pdf_data`
            table, used to associate the processed images with the original
            PDF.

    Returns:
        None

    The function performs the following steps:
        1. Convert the PDF BLOB into images.
        2. For each image:
            - Store the initial raw image and extract OCR text.
            - Apply grayscale preprocessing, store the image, and extract OCR text.
            - Apply Otsu thresholding preprocessing, store the image, and extract OCR text.
            - Apply denoising preprocessing, store the image, and extract OCR text.

    Example usage:
        pdf_blob = ...  # Retrieved from the database
        pdf_data_id = 1  # The ID from the pdf_data table corresponding to this PDF
        process_and_store_image(pdf_blob, pdf_data_id)
    """
    # Initialize components
    pdf_converter = PDFConverter(pdf_blob)
    image_processor = ImageProcessor()
    image_storage = ImageStorage(db_path="use_cases.duckdb")
    ocr_extractor = OCRTextExtractor()

    # Convert PDF to images (assuming only one image here for simplicity)
    images = pdf_converter.convert_to_images()

    for image in images:
        # Store the initial raw image
        raw_text = ocr_extractor.extract_text(image)
        image_storage.save_image_blob(pdf_data_id, image, "initial_raw", raw_text)

        # Grayscale preprocessing
        grayscale_image = image_processor.preprocess_image(
            np.array(image), method="grayscale"
        )
        grayscale_text = ocr_extractor.extract_text(grayscale_image)
        image_storage.save_image_blob(
            pdf_data_id, grayscale_image, "grayscale", grayscale_text
        )

        # Otsu thresholding preprocessing
        threshold_image = image_processor.preprocess_image(
            grayscale_image, method="threshold"
        )
        threshold_text = ocr_extractor.extract_text(threshold_image)
        image_storage.save_image_blob(
            pdf_data_id, threshold_image, "otsu_threshold", threshold_text
        )

        # Denoising preprocessing
        denoised_image = image_processor.preprocess_image(
            threshold_image, method="denoise"
        )
        denoised_text = ocr_extractor.extract_text(denoised_image)
        image_storage.save_image_blob(
            pdf_data_id, denoised_image, "denoise", denoised_text
        )


# Example usage:
if __name__ == "__main__":
    db_path = "use_cases.duckdb"
    # Retrieve the PDF BLOB from the database (assuming you've done this)
    pdf_blob = ...  # Retrieved from the database
    pdf_data_id = 1  # The ID from the pdf_data table corresponding to this PDF
    process_and_store_image(pdf_blob, pdf_data_id)
