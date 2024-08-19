from src.utils.selenium_helper import WebAutomationHelper


class PDFSiteScraper:
    """
    Contains the specific steps to download PDFs from a website using Selenium.
    """

    def __init__(self, helper: WebAutomationHelper):
        """
        Initializes the PDFSiteScraper with a WebAutomationHelper.

        Args:
            helper (WebAutomationHelper): The helper instance to interact with the website.
        """
        self.helper = helper

    def download_pdf(
        self, acctnumber: str, checknumber: str, amount: str, date: str
    ) -> str:
        """
        Executes the steps needed to download a PDF file.

        Args:
            acctnumber (str): The account number.
            checknumber (str): The check number.
            amount (str): The amount associated with the check.
            date (str): The date of the check.

        Returns:
            str: The path to the downloaded PDF.
        """
        # Navigate to the target page
        self.helper.navigate_to()

        # Input the necessary data into the form fields
        self.helper.input_data("acct_number", acctnumber)
        self.helper.input_data("check_number", checknumber)
        self.helper.input_data("amount", amount)
        self.helper.input_data("date", date)

        # Click the search button to initiate the search
        self.helper.click_element("search_button")

        # Switch to the new window or frame that contains the download button
        self.helper.switch_to_new_window()

        # Click the download button to download the PDF
        self.helper.click_element("popup_download_button")

        # Wait for the download to complete (implement logic to confirm download completion)
        self.helper.wait_for_element("popup_download_button")

        # Return the path to the downloaded file (assumed standard path)
        return "data/tmp/image.pdf"
