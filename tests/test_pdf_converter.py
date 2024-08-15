"""
This script contains unit tests for the `PDFConverter` class using the pytest 
framework. The tests ensure that the class initializes correctly and that the 
PDF conversion to images works as expected.

Fixtures:
    sample_pdf_blob: Provides a sample PDF BLOB for testing.

Tests:
    test_initialization: Verifies that the `PDFConverter` class initializes 
        correctly with the provided PDF BLOB.
    test_convert_to_images: Tests the `convert_to_images` method to ensure it 
        returns a list of images, where each image has a `size` attribute.

Modules:
    - pdf_converter: Contains the `PDFConverter` class responsible for 
      converting PDF BLOBs into images.

Example usage:
    pytest test_pdf_converter.py
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from pdf_converter import PDFConverter


@pytest.fixture
def sample_pdf_blob():
    """
    Fixture to provide a sample PDF BLOB for testing.

    Returns:
        bytes: A sample PDF BLOB.
    """
    # A valid sample PDF BLOB for testing
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog /Pages 2 0 R >>\n"
        b"endobj\n"
        b"2 0 obj\n"
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
        b"endobj\n"
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\n"
        b"endobj\n"
        b"4 0 obj\n"
        b"<< /Length 55 >>\n"
        b"stream\n"
        b"BT\n"
        b"/F1 24 Tf\n"
        b"100 700 Td\n"
        b"(Hello, World!) Tj\n"
        b"ET\n"
        b"endstream\n"
        b"endobj\n"
        b"xref\n"
        b"0 5\n"
        b"0000000000 65535 f \n"
        b"0000000010 00000 n \n"
        b"0000000053 00000 n \n"
        b"0000000102 00000 n \n"
        b"0000000175 00000 n \n"
        b"trailer\n"
        b"<< /Root 1 0 R /Size 5 >>\n"
        b"startxref\n"
        b"256\n"
        b"%%EOF\n"
    )


def test_initialization(sample_pdf_blob):
    """
    Test the initialization of the `PDFConverter` class.

    Args:
        sample_pdf_blob (bytes): The sample PDF BLOB fixture.

    Raises:
        AssertionError: If the PDF BLOB is not correctly assigned to the
            `pdf_blob` attribute of the `PDFConverter` instance.
    """
    pdf_converter = PDFConverter(sample_pdf_blob)
    assert pdf_converter.pdf_blob == sample_pdf_blob


def test_convert_to_images(sample_pdf_blob):
    """
    Test the `convert_to_images` method of the `PDFConverter` class.

    Args:
        sample_pdf_blob (bytes): The sample PDF BLOB fixture.

    Raises:
        AssertionError: If the method does not return a list of images or if
            any image in the list does not have a `size` attribute.
    """
    pdf_converter = PDFConverter(sample_pdf_blob)
    images = pdf_converter.convert_to_images()
    assert isinstance(images, list)
    assert len(images) > 0
    for image in images:
        assert hasattr(image, "size")  # Check if the image has a size attribute
