import os
import sys

# Ensure the src directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from PIL import Image

from ocr_workflow import process_and_store_image


@pytest.fixture
def mock_pdf_converter():
    with patch("ocr_workflow.PDFConverter") as MockPDFConverter:
        yield MockPDFConverter


@pytest.fixture
def mock_image_processor():
    with patch("ocr_workflow.ImageProcessor") as MockImageProcessor:
        yield MockImageProcessor


@pytest.fixture
def mock_image_storage():
    with patch("ocr_workflow.ImageStorage") as MockImageStorage:
        yield MockImageStorage


@pytest.fixture
def mock_ocr_extractor():
    with patch("ocr_workflow.OCRTextExtractor") as MockOCRTextExtractor:
        yield MockOCRTextExtractor


def test_process_and_store_image(
    mock_pdf_converter, mock_image_processor, mock_image_storage, mock_ocr_extractor
):
    # Arrange
    pdf_blob = b"%PDF-1.4..."  # Example PDF BLOB
    pdf_data_id = 1

    mock_pdf_converter_instance = mock_pdf_converter.return_value
    mock_image_processor_instance = mock_image_processor.return_value
    mock_image_storage_instance = mock_image_storage.return_value
    mock_ocr_extractor_instance = mock_ocr_extractor.return_value

    # Mock the conversion of PDF to images
    mock_image = Image.new("RGB", (100, 100), color="white")
    mock_pdf_converter_instance.convert_to_images.return_value = [mock_image]

    # Mock the OCR text extraction
    mock_ocr_extractor_instance.extract_text.return_value = "mocked text"

    # Mock the image preprocessing
    mock_image_processor_instance.preprocess_image.side_effect = lambda img, method: img

    # Act
    process_and_store_image(pdf_blob, pdf_data_id)

    # Assert
    mock_pdf_converter_instance.convert_to_images.assert_called_once_with()
    mock_ocr_extractor_instance.extract_text.assert_called()
    mock_image_storage_instance.save_image_blob.assert_called()

    # Check that the image preprocessing methods were called
    assert mock_image_processor_instance.preprocess_image.call_count == 3

    # Check that the OCR text extraction was called for each processed image
    assert mock_ocr_extractor_instance.extract_text.call_count == 4

    # Check that the images were saved with the correct labels
    save_calls = mock_image_storage_instance.save_image_blob.call_args_list
    assert save_calls[0][0][2] == "initial_raw"
    assert save_calls[1][0][2] == "grayscale"
    assert save_calls[2][0][2] == "otsu_threshold"
    assert save_calls[3][0][2] == "denoise"
