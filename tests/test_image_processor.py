import os
import sys

# Ensure the src directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import cv2
import numpy as np
import pytest
from image_processor import ImageProcessor


@pytest.fixture
def sample_image():
    """
    Fixture to provide a sample image for testing.

    Returns:
        numpy.ndarray: A sample image.
    """
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(image, (25, 25), (75, 75), (255, 255, 255), -1)  # Add a white square
    return image


def test_preprocess_image_grayscale(sample_image):
    """
    Test the 'grayscale' preprocessing method of the `ImageProcessor` class.

    Args:
        sample_image (numpy.ndarray): The sample image fixture.
    """
    processor = ImageProcessor()
    gray_image = processor.preprocess_image(sample_image, method="grayscale")
    assert len(gray_image.shape) == 2, "The image should be converted to grayscale."


def test_preprocess_image_threshold(sample_image):
    """
    Test the 'threshold' preprocessing method of the `ImageProcessor` class.

    Args:
        sample_image (numpy.ndarray): The sample image fixture.
    """
    processor = ImageProcessor()
    thresh_image = processor.preprocess_image(sample_image, method="threshold")
    assert (
        len(thresh_image.shape) == 2
    ), "The image should be thresholded to a binary image."
    assert np.unique(thresh_image).tolist() == [
        0,
        255,
    ], "The thresholded image should only contain 0 and 255."


def test_preprocess_image_denoise(sample_image):
    """
    Test the 'denoise' preprocessing method of the `ImageProcessor` class.

    Args:
        sample_image (numpy.ndarray): The sample image fixture.
    """
    processor = ImageProcessor()
    denoised_image = processor.preprocess_image(sample_image, method="denoise")
    assert (
        denoised_image.shape == sample_image.shape
    ), "The denoised image should have the same shape as the input image."


def test_preprocess_image_invalid_method(sample_image):
    """
    Test the `preprocess_image` method with an invalid preprocessing method.

    Args:
        sample_image (numpy.ndarray): The sample image fixture.
    """
    processor = ImageProcessor()
    with pytest.raises(ValueError, match="Unknown preprocessing method: invalid"):
        processor.preprocess_image(sample_image, method="invalid")
