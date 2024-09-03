import logging
from typing import Any, Dict, Optional

from selenium import webdriver
from selenium.common.exceptions import JavascriptException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Constants
DEFAULT_TIMEOUT = 30
DEFAULT_DOWNLOAD_DIR = "data/temp/"


class WebAutomationHelper:
    """A helper class to automate web interactions using Selenium WebDriver.

    This class handles browser setup, navigation, form filling,
    element interactions, and window management.

    Attributes:
        config (Dict[str, Any]): Configuration dictionary loaded from a JSON file,
            containing the URL, selectors, and frames.
        driver (webdriver.Chrome): The Chrome WebDriver instance used for automation.
        main_window (Optional[str]): The handle of the main window for switching
            between windows.
        logger (logging.Logger): Logger instance for this class.
    """

    def __init__(self, config: Dict[str, Any], download_dir: Optional[str] = None):
        """Initialize the WebAutomationHelper class.

        Args:
            config: The configuration dictionary containing the URL,
                selectors, and frames.
            download_dir: The directory where files will be downloaded.
                If not specified, uses the default directory.
        """
        self.config = config
        self.driver = self._setup_driver(download_dir or DEFAULT_DOWNLOAD_DIR)
        self.main_window: Optional[str] = None
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def _setup_driver(self, download_dir: str) -> webdriver.Chrome:
        """Set up Chrome WebDriver with specified download directory.

        Args:
            download_dir: The directory where downloads should be saved.

        Returns:
            A configured Chrome WebDriver instance.
        """
        options = webdriver.ChromeOptions()
        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "download.default_directory": download_dir,
        }
        options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(options=options)

    def navigate_to(self) -> None:
        """Navigate to the URL from the config."""
        self.driver.get(self.config["url"])
        self.main_window = self.driver.current_window_handle

    def input_data(
        self, acctnumber: str, checknumber: str, amount: str, date: str
    ) -> None:
        """Input data into the respective fields on the website.

        Args:
            acctnumber: The account number to input.
            checknumber: The check number to input.
            amount: The amount to input.
            date: The date to input.
        """
        self.driver.find_element(
            By.CSS_SELECTOR, self.config["selectors"]["acct_number"]
        ).send_keys(acctnumber)
        self.driver.find_element(
            By.CSS_SELECTOR, self.config["selectors"]["check_number"]
        ).send_keys(checknumber)
        self.driver.find_element(
            By.CSS_SELECTOR, self.config["selectors"]["amount"]
        ).send_keys(amount)
        self.driver.find_element(
            By.CSS_SELECTOR, self.config["selectors"]["date"]
        ).send_keys(date)

    def click_element(self, element_name: str) -> None:
        """Click an element specified by a selector from the config.

        Args:
            element_name: The name of the element in the config's selectors.
        """
        selector = self.config["selectors"][element_name]
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        element.click()

    def wait_for_element(
        self, element_name: str, timeout: int = DEFAULT_TIMEOUT
    ) -> Any:
        """Wait for an element to be clickable and return it.

        Args:
            element_name: The name of the element in the config's selectors.
            timeout: The maximum time to wait for the element.

        Returns:
            The WebElement once it is clickable.

        Raises:
            TimeoutException: If the element is not clickable within the timeout period.
        """
        selector = self.config["selectors"][element_name]
        wait = WebDriverWait(self.driver, timeout)
        try:
            return wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        except TimeoutException:
            self.logger.error(f"Timeout waiting for element: {element_name}")
            raise

    def switch_to_frame(self, frame_name: str) -> None:
        """Switch to a specified frame from the config.

        Args:
            frame_name: The name of the frame in the config's frames.
        """
        frame_index = self.config["frames"][frame_name]
        self.driver.switch_to.frame(frame_index)

    def switch_to_default_content(self) -> None:
        """Switch back to the main content (default frame)."""
        self.driver.switch_to.default_content()

    def switch_to_new_window(self) -> None:
        """Switch to the newest window or pop-up."""
        wait = WebDriverWait(self.driver, DEFAULT_TIMEOUT)
        wait.until(EC.number_of_windows_to_be(2))
        new_window = [
            window
            for window in self.driver.window_handles
            if window != self.main_window
        ][0]
        self.driver.switch_to.window(new_window)

    def switch_to_main_window(self) -> None:
        """Switch back to the main window."""
        if self.main_window:
            self.driver.switch_to.window(self.main_window)
        else:
            self.logger.warning("Main window handle is not set.")

    def close_window(self) -> None:
        """Close the current window."""
        self.driver.close()

    def quit(self) -> None:
        """Quit the WebDriver and close all windows."""
        self.driver.quit()

    def execute_javascript(self, script: str, *args: Any) -> Any:
        """Execute JavaScript code in the current browser context.

        Args:
            script: The JavaScript code to execute.
            *args: Variable length argument list for any parameters to be passed to the script.

        Returns:
            The result of the JavaScript execution.

        Raises:
            JavascriptException: If there's an error in JavaScript execution.
        """
        try:
            return self.driver.execute_script(script, *args)
        except JavascriptException as e:
            self.logger.error(f"Error executing JavaScript: {e}")
            raise
