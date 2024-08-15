import cv2
import numpy as np
import pytesseract
from PIL import Image


class OCRTextExtractor:
    """
    A class to extract text from images using Tesseract OCR.

    Methods:
        extract_text(image):
            Extract text from the given image using Tesseract OCR.
    """

    def extract_text(self, image):
        """
        Extract text from the image using Tesseract OCR.

        Args:
            image (numpy.ndarray or PIL.Image.Image): The image from which to
                extract text. It can be in either OpenCV format (numpy array)
                or PIL format.

        Returns:
            str: The extracted text from the image.

        Example usage:
            ocr_extractor = OCRTextExtractor()
            text = ocr_extractor.extract_text(image)
        """
        # If the image is a numpy array (OpenCV format), convert it to PIL format
        if not isinstance(image, (Image.Image, np.ndarray)):
            raise AttributeError("Invalid image type")
        text = pytesseract.image_to_string(image)
        return text
