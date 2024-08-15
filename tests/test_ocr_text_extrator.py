import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest
from PIL import Image

from ocr_text_extractor import OCRTextExtractor


@pytest.fixture
def ocr_extractor():
    return OCRTextExtractor()


def test_extract_text_from_pil_image(ocr_extractor):
    pil_image = Image.new("RGB", (100, 100), color="white")
    with patch("pytesseract.image_to_string", return_value="mocked text") as mock_ocr:
        text = ocr_extractor.extract_text(pil_image)
        mock_ocr.assert_called_once_with(pil_image)
        assert text == "mocked text"


def test_extract_text_from_cv2_image(ocr_extractor):
    cv2_image = np.zeros((100, 100, 3), dtype=np.uint8)
    with patch("pytesseract.image_to_string", return_value="mocked text") as mock_ocr:
        text = ocr_extractor.extract_text(cv2_image)
        assert mock_ocr.call_count == 1
        assert text == "mocked text"


def test_extract_text_invalid_image_type(ocr_extractor):
    invalid_image = "not an image"
    with pytest.raises(AttributeError):
        ocr_extractor.extract_text(invalid_image)
