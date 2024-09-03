import os
from typing import Optional

from src.utils.selenium_helper import WebAutomationHelper


class PDFSiteScraper:
    """
    Contains the specific steps to download PDFs from a website using Selenium.
    """

    def __init__(self, helper: WebAutomationHelper):
        """
        Initializes the PDFSiteScraper with a WebAutomationHelper.

        Args:
            helper (WebAutomationHelper): The helper instance to interact with
                the website.
        """
        self.helper = helper

    def download_pdf(
        self, acctnumber: str, checknumber: str, amount: str, date: str, temp_dir: str
    ) -> Optional[str]:
        """
        Executes the steps needed to download a PDF file.

        Args:
            acctnumber (str): The account number associated with the PDF.
            checknumber (str): The check number associated with the PDF.
            amount (str): The amount associated with the check.
            date (str): The date of the check.
            temp_dir (str): The temporary directory to store the downloaded
                PDF.

        Returns:
            The path to the downloaded PDF, or None if no results are found.
        """
        # Navigate to the target page
        self.helper.navigate_to()

        # Input the necessary data into the form fields
        self._input_form_data(acctnumber, checknumber, amount, date)

        # Click the search button to initiate the search
        self.helper.click_element("search_button")

        # Handle potential scenarios
        if self._handle_no_results_scenario():
            return None

        if self._handle_alternative_popup_scenario(temp_dir):
            # If we handled an alternative popup, return early
            return os.path.join(temp_dir, "Image.pdf")

        # Switch to the new window or frame that contains the download button
        self.helper.switch_to_new_window()

        # Click the download button to download the PDF
        self.helper.click_element("popup_download_button")

        # Wait for the download to complete (implement logic to confirm download completion)
        self.helper.wait_for_element("popup_download_button")

        # Assume the downloaded file is always named "Image.pdf" in the temp dir
        return os.path.join(temp_dir, "Image.pdf")

    def _input_form_data(
        self, acctnumber: str, checknumber: str, amount: str, date: str
    ) -> None:
        """
        Input the necessary data into the form fields.
        """
        self.helper.input_data("acct_number", acctnumber)
        self.helper.input_data("check_number", checknumber)
        self.helper.input_data("amount", amount)
        self.helper.input_data("date", date)

    def _handle_no_results_scenario(self) -> bool:
        """
        Check if the "No Results" message is displayed and handle it.

        Returns:
            True if the "No Results" scenario was handled, False otherwise.
        """
        no_results_selector = "div.no-results"  # Replace with the actual selector
        if self.helper.element_exists(no_results_selector):
            print("No Results Found for the provided criteria.")
            return True
        return False

    def _handle_alternative_popup_scenario(self, temp_dir: str) -> bool:
        """
        Check for an alternative popup and handle it if present.

        Args:
            temp_dir (str): The temporary directory to store the downloaded PDF.

        Returns:
            True if an alternative popup was handled, False otherwise.
        """
        alternative_popup_selector = (
            "#alternative_popup"  # Replace with the actual selector
        )
        if self.helper.element_exists(alternative_popup_selector):
            print("Alternative popup detected. Handling the scenario.")
            self.helper.click_element("alternative_button")

            # Now, assume this leads to the normal download popup
            self.helper.switch_to_new_window()
            self.helper.click_element("popup_download_button")
            self.helper.wait_for_element("popup_download_button")
            return True
        return False
