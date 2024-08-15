"""
This script contains unit tests for the `ImageStorage` class, specifically 
testing the `save_image_blob` method using pytest and unittest's mocking 
capabilities. The tests verify that the method correctly stores images as 
BLOBs in the database, both with and without OCR text.

Fixtures:
    mock_db: Mocks the SQLite database connection and cursor.
    mock_cv2: Mocks the `cv2.imencode` function to simulate image encoding 
        without using actual image files.

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

# Ensure the src directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import sqlite3
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest

from src.image_storage import ImageStorage


@pytest.fixture
def mock_db():
    """
    Fixture to mock the SQLite database connection and cursor.

    Returns:
        MagicMock: Mocked SQLite cursor object.
    """
    with patch("sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        yield mock_cursor


@pytest.fixture
def mock_cv2():
    """
    Fixture to mock the cv2 library functions.

    Returns:
        MagicMock: Mocked `cv2.imencode` function.
    """
    with patch("cv2.imencode") as mock_imencode:
        mock_imencode.return_value = (True, np.array([1, 2, 3]))
        yield mock_imencode


def test_save_image_blob(mock_db, mock_cv2):
    """
    Test the `save_image_blob` method of the `ImageStorage` class.

    Args:
        mock_db (MagicMock): Mocked SQLite cursor object.
        mock_cv2 (MagicMock): Mocked `cv2.imencode` function.

    Raises:
        AssertionError: If the method does not insert the expected data into
            the database.
    """
    storage = ImageStorage(db_path="test.db")
    pdf_data_id = 1
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    processing_type = "grayscale"
    ocr_text = "sample OCR text"

    storage.save_image_blob(pdf_data_id, image, processing_type, ocr_text)

    mock_db.execute.assert_called_once_with(
        """
        INSERT INTO ocr_images (pdf_data_id, image_blob, ocr_text, processing_type)
        VALUES (?, ?, ?, ?)""",
        (pdf_data_id, mock_cv2.return_value[1].tobytes(), ocr_text, processing_type),
    )
    mock_db.connection.commit.assert_called_once()
    mock_db.connection.close.assert_called_once()


def test_save_image_blob_without_ocr_text(mock_db, mock_cv2):
    """
    Test the `save_image_blob` method of the `ImageStorage` class without
    OCR text.

    Args:
        mock_db (MagicMock): Mocked SQLite cursor object.
        mock_cv2 (MagicMock): Mocked `cv2.imencode` function.

    Raises:
        AssertionError: If the method does not insert the expected data into
            the database when no OCR text is provided.
    """
    storage = ImageStorage(db_path="test.db")
    pdf_data_id = 1
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    processing_type = "grayscale"

    storage.save_image_blob(pdf_data_id, image, processing_type)

    mock_db.execute.assert_called_once_with(
        """
        INSERT INTO ocr_images (pdf_data_id, image_blob, ocr_text, processing_type)
        VALUES (?, ?, ?, ?)""",
        (pdf_data_id, mock_cv2.return_value[1].tobytes(), None, processing_type),
    )
    mock_db.connection.commit.assert_called_once()
    mock_db.connection.close.assert_called_once()
