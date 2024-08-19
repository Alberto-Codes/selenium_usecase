import json
import os
import tempfile

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class WebAutomationHelper:
    """
    A helper class to automate web interactions using Selenium WebDriver.
    This class handles browser setup, navigation, form filling,
    element interactions, and window management.

    Attributes:
        config (dict): Configuration dictionary loaded from a JSON file,
            containing the URL, selectors, and frames.
        driver (webdriver.Chrome): The Chrome WebDriver instance used for
            automation.
        main_window (str): The handle of the main window for switching
            between windows.

    Methods:
        navigate_to(): Navigate to the URL specified in the config.
        input_data(acctnumber, checknumber, amount, date): Input data into
            the respective fields on the website.
        click_element(element_name): Click an element specified by a selector
            in the config.
        wait_for_element(element_name, timeout=30): Wait for an element to be
            clickable and return it.
        switch_to_frame(frame_name): Switch to a specified frame.
        switch_to_default_content(): Switch back to the main content (default
            frame).
        switch_to_new_window(): Switch to the newest window or pop-up.
        switch_to_main_window(): Switch back to the main window.
        close_window(): Close the current window.
        quit(): Quit the WebDriver and close all windows.
    """

    def __init__(self, config, download_dir="data/temp/"):
        """
        Initialize the WebAutomationHelper class.

        Args:
            config (dict): The configuration dictionary containing the URL,
                selectors, and frames.
            download_dir (str, optional): The directory where files will be
                downloaded. If not specified, uses the default directory.
        """
        self.config = config
        self.driver = self._setup_driver(download_dir)
        self.main_window = None

    def _setup_driver(self, download_dir):
        """Set up Chrome WebDriver with specified download directory."""
        options = webdriver.ChromeOptions()
        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }

        if download_dir:
            prefs["download.default_directory"] = download_dir

        options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(options=options)

    def navigate_to(self):
        """Navigate to the URL from the config."""
        self.driver.get(self.config["url"])
        self.main_window = self.driver.current_window_handle

    def input_data(self, acctnumber, checknumber, amount, date):
        """Input data into the respective fields on the website."""
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

    def click_element(self, element_name):
        """Click an element specified by a selector from the config."""
        selector = self.config["selectors"][element_name]
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        element.click()

    def wait_for_element(self, element_name, timeout=30):
        """Wait for an element to be clickable and return it."""
        selector = self.config["selectors"][element_name]
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))

    def switch_to_frame(self, frame_name):
        """Switch to a specified frame from the config."""
        frame_index = self.config["frames"][frame_name]
        self.driver.switch_to.frame(frame_index)

    def switch_to_default_content(self):
        """Switch back to the main content (default frame)."""
        self.driver.switch_to.default_content()

    def switch_to_new_window(self):
        """Switch to the newest window or pop-up."""
        wait = WebDriverWait(self.driver, 30)
        wait.until(EC.number_of_windows_to_be(2))
        new_window = [
            window
            for window in self.driver.window_handles
            if window != self.main_window
        ][0]
        self.driver.switch_to.window(new_window)

    def switch_to_main_window(self):
        """Switch back to the main window."""
        self.driver.switch_to.window(self.main_window)

    def close_window(self):
        """Close the current window."""
        self.driver.close()

    def quit(self):
        """Quit the WebDriver and close all windows."""
        self.driver.quit()
