"""
This script contains unit tests for the `ImageStorage` class, specifically
testing the `save_image_blob` method using pytest and unittest's mocking
capabilities. The tests verify that the method correctly stores images as
BLOBs in the database, both with and without OCR text.

Tests:
    test_save_image_blob: Tests the `save_image_blob` method to ensure it
        correctly inserts an image BLOB with associated processing type and
        OCR text into the database.
    test_save_image_blob_without_ocr_text: Tests the `save_image_blob` method
        to ensure it correctly inserts an image BLOB with associated
        processing type into the database without OCR text.

Modules:
    - image_storage: Contains the `ImageStorage` class responsible for
      storing images as BLOBs in the database.

Example usage:
    pytest test_image_storage.py
"""

import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from unittest.mock import MagicMock, patch

import numpy as np
from image_storage import ImageStorage


@patch("image_storage.cv2.imencode", return_value=(True, MagicMock()))
@patch("image_storage.sqlite3.connect")
def test_save_image_blob(mock_connect, mock_imencode):
    """
    Test the `save_image_blob` method of the `ImageStorage` class to ensure
    it correctly inserts an image BLOB with associated processing type and
    OCR text into the database.

    Args:
        mock_connect (MagicMock): Mocked SQLite connection object.
        mock_imencode (MagicMock): Mocked `cv2.imencode` function.

    Raises:
        AssertionError: If the method does not insert the expected data into
            the database or if the database commit and close operations are
            not called.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    storage = ImageStorage(db_path="test.db")
    pdf_data_id = 1
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    processing_type = "grayscale"
    ocr_text = "sample OCR text"

    storage.save_image_blob(pdf_data_id, processing_type, image, ocr_text)

    mock_cursor.execute.assert_called_once_with(
        """
        INSERT INTO ocr_images (pdf_data_id, processing_type, image_blob, ocr_text)
        VALUES (?, ?, ?, ?)""",
        (
            pdf_data_id,
            processing_type,
            mock_imencode.return_value[1].tobytes(),
            ocr_text,
        ),
    )
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("image_storage.cv2.imencode", return_value=(True, MagicMock()))
@patch("image_storage.sqlite3.connect")
def test_save_image_blob_without_ocr_text(mock_connect, mock_imencode):
    """
    Test the `save_image_blob` method of the `ImageStorage` class to ensure
    it correctly inserts an image BLOB with associated processing type into
    the database without OCR text.

    Args:
        mock_connect (MagicMock): Mocked SQLite connection object.
        mock_imencode (MagicMock): Mocked `cv2.imencode` function.

    Raises:
        AssertionError: If the method does not insert the expected data into
            the database or if the database commit and close operations are
            not called.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    storage = ImageStorage(db_path="test.db")
    pdf_data_id = 1
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    processing_type = "grayscale"

    storage.save_image_blob(pdf_data_id, processing_type, image)

    mock_cursor.execute.assert_called_once_with(
        """
        INSERT INTO ocr_images (pdf_data_id, processing_type, image_blob, ocr_text)
        VALUES (?, ?, ?, ?)""",
        (pdf_data_id, processing_type, mock_imencode.return_value[1].tobytes(), None),
    )
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
