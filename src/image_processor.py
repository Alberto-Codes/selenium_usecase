import cv2


class ImageProcessor:
    """
    A class for preprocessing images using various methods such as grayscale
    conversion, thresholding, and denoising.

    Methods:
        preprocess_image(image, method='grayscale'):
            Apply preprocessing to the image based on the specified method.
    """

    def preprocess_image(self, image, method="grayscale"):
        """
        Apply preprocessing to the image based on the specified method.

        Args:
            image (numpy.ndarray): The input image to preprocess.
            method (str): The preprocessing method to apply. Options include
                'grayscale', 'threshold', and 'denoise'. Defaults to 'grayscale'.

        Returns:
            numpy.ndarray: The preprocessed image.

        Raises:
            ValueError: If an unknown preprocessing method is specified.

        Available methods:
            - 'grayscale': Convert the image to grayscale.
            - 'threshold': Apply binary thresholding using Otsu's method.
            - 'denoise': Apply Non-Local Means denoising.

        Example usage:
            image_processor = ImageProcessor()
            gray_image = image_processor.preprocess_image(image, method='grayscale')
        """
        if method == "grayscale":
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif method == "threshold":
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(
                gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            return thresh
        elif method == "denoise":
            return cv2.fastNlMeansDenoising(image, h=30)
        else:
            raise ValueError(f"Unknown preprocessing method: {method}")
