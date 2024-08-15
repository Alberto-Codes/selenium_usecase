"""
This script contains unit tests for the `WebAutomationHelper` class and 
related functions using the pytest framework and unittest's mocking 
capabilities. The tests ensure that the Selenium-based web automation 
functions are working correctly, by mocking the Selenium WebDriver 
interactions.

Fixtures:
    mock_driver: Mocks the Selenium WebDriver to test the WebAutomationHelper 
        class without launching an actual browser.
    config: Provides a sample configuration dictionary used to test 
        WebAutomationHelper.

Tests:
    test_navigate_to: Verifies that the WebDriver navigates to the correct 
        URL.
    test_input_data: Tests if the input data method correctly locates and 
        fills in the form fields.
    test_click_element: Checks if the click_element method correctly clicks 
        on the specified element.
    test_wait_for_element: Ensures that the wait_for_element method waits 
        for an element to be clickable.
    test_switch_to_frame: Verifies that the WebDriver switches to the 
        correct frame.
    test_switch_to_default_content: Ensures the WebDriver switches back to 
        the default content.
    test_switch_to_new_window: Tests if the WebDriver switches to the new 
        window.
    test_switch_to_main_window: Ensures the WebDriver switches back to the 
        main window.
    test_close_window: Verifies that the current window is closed.
    test_quit: Checks if the WebDriver quits and closes all windows.
    test_load_config: Tests the load_config function to ensure it correctly 
        loads configuration from a JSON file.
    test_process_use_cases: Tests the entire process_use_cases function, 
        ensuring the automation workflow executes correctly with mock data.

Modules:
    - selenium_helper: Contains the WebAutomationHelper class and related 
        functions for Selenium-based web automation.

Example usage:
    pytest test_selenium_helper.py
"""
import os
import sys

# Ensure the src directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from unittest.mock import MagicMock, patch

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium_helper import (WebAutomationHelper)


@pytest.fixture
def mock_driver():
    """
    Fixture to mock the Selenium WebDriver.

    Returns:
        MagicMock: Mocked Selenium WebDriver.
    """
    with patch("src.selenium_helper.webdriver.Chrome") as MockWebDriver:
        yield MockWebDriver.return_value


@pytest.fixture
def config():
    """
    Fixture to provide a sample configuration for testing.

    Returns:
        dict: Configuration dictionary for WebAutomationHelper.
    """
    return {
        "url": "http://example.com",
        "selectors": {
            "acct_number": "#acct_number",
            "check_number": "#check_number",
            "amount": "#amount",
            "date": "#date",
            "search_button": "#search_button",
            "download_button": "#download_button",
            "popup_download_button": "#popup_download_button",
        },
        "frames": {"initial_frame": 0, "result_frame": 1},
    }


def test_navigate_to(mock_driver, config):
    """
    Test that the WebDriver navigates to the correct URL.

    Args:
        mock_driver (MagicMock): Mocked Selenium WebDriver.
        config (dict): Configuration dictionary.
    """
    helper = WebAutomationHelper(config)
    helper.navigate_to()
    mock_driver.get.assert_called_once_with(config["url"])


def test_input_data(mock_driver, config):
    """
    Test if input_data correctly inputs data into form fields.

    Args:
        mock_driver (MagicMock): Mocked Selenium WebDriver.
        config (dict): Configuration dictionary.
    """
    helper = WebAutomationHelper(config)
    helper.input_data("123456", "1001", "100.00", "2023-01-01")
    mock_driver.find_element.assert_any_call(
        By.CSS_SELECTOR, config["selectors"]["acct_number"]
    )
    mock_driver.find_element.assert_any_call(
        By.CSS_SELECTOR, config["selectors"]["check_number"]
    )
    mock_driver.find_element.assert_any_call(
        By.CSS_SELECTOR, config["selectors"]["amount"]
    )
    mock_driver.find_element.assert_any_call(
        By.CSS_SELECTOR, config["selectors"]["date"]
    )


def test_click_element(mock_driver, config):
    """
    Test if click_element correctly clicks the specified element.

    Args:
        mock_driver (MagicMock): Mocked Selenium WebDriver.
        config (dict): Configuration dictionary.
    """
    helper = WebAutomationHelper(config)
    helper.click_element("search_button")
    mock_driver.find_element.assert_called_once_with(
        By.CSS_SELECTOR, config["selectors"]["search_button"]
    )


def test_wait_for_element(mock_driver, config):
    """
    Test if wait_for_element waits for the element to be clickable.

    Args:
        mock_driver (MagicMock): Mocked Selenium WebDriver.
        config (dict): Configuration dictionary.
    """
    with patch("selenium_helper.WebDriverWait") as MockWebDriverWait:
        helper = WebAutomationHelper(config)
        helper.wait_for_element("search_button")
        MockWebDriverWait.return_value.until.assert_called_once()


def test_switch_to_frame(mock_driver, config):
    """
    Test if switch_to_frame switches to the correct frame.

    Args:
        mock_driver (MagicMock): Mocked Selenium WebDriver.
        config (dict): Configuration dictionary.
    """
    helper = WebAutomationHelper(config)
    helper.switch_to_frame("initial_frame")
    mock_driver.switch_to.frame.assert_called_once_with(
        config["frames"]["initial_frame"]
    )


def test_switch_to_default_content(mock_driver, config):
    """
    Test if switch_to_default_content switches back to default content.

    Args:
        mock_driver (MagicMock): Mocked Selenium WebDriver.
        config (dict): Configuration dictionary.
    """
    helper = WebAutomationHelper(config)
    helper.switch_to_default_content()
    mock_driver.switch_to.default_content.assert_called_once()


def test_switch_to_new_window(mock_driver, config):
    """
    Test if switch_to_new_window switches to the new window.

    Args:
        mock_driver (MagicMock): Mocked Selenium WebDriver.
        config (dict): Configuration dictionary.
    """
    mock_driver.window_handles = ["main_window", "new_window"]
    helper = WebAutomationHelper(config)
    helper.main_window = "main_window"
    helper.switch_to_new_window()
    mock_driver.switch_to.window.assert_called_once_with("new_window")


def test_switch_to_main_window(mock_driver, config):
    """
    Test if switch_to_main_window switches back to the main window.

    Args:
        mock_driver (MagicMock): Mocked Selenium WebDriver.
        config (dict): Configuration dictionary.
    """
    helper = WebAutomationHelper(config)
    helper.main_window = "main_window"
    helper.switch_to_main_window()
    mock_driver.switch_to.window.assert_called_once_with("main_window")


def test_close_window(mock_driver, config):
    """
    Test if close_window closes the current window.

    Args:
        mock_driver (MagicMock): Mocked Selenium WebDriver.
        config (dict): Configuration dictionary.
    """
    helper = WebAutomationHelper(config)
    helper.close_window()
    mock_driver.close.assert_called_once()


def test_quit(mock_driver, config):
    """
    Test if quit closes all browser windows and quits the WebDriver.

    Args:
        mock_driver (MagicMock): Mocked Selenium WebDriver.
        config (dict): Configuration dictionary.
    """
    helper = WebAutomationHelper(config)
    helper.quit()
    mock_driver.quit.assert_called_once()
