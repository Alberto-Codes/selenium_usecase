"""
This script contains unit tests for the `download_manager` module, 
including the functions `download_pdf_with_selenium`, `load_config`, and 
`process_rows_for_download`. The tests use pytest and unittest.mock to 
mock dependencies such as database connections and Selenium WebDriver, 
allowing for isolated and controlled testing of the module's functionality.

Fixtures:
    mock_db: Mocks the SQLite database connection and cursor for testing 
        database interactions.
    mock_helper: Mocks the WebAutomationHelper class to test Selenium-based 
        functions without launching a real browser.

Tests:
    test_load_config: Tests the `load_config` function to ensure it correctly 
        loads configuration from a JSON file.
    test_process_rows_for_download: Tests the `process_rows_for_download` 
        function to verify that it processes database rows correctly, 
        including downloading PDFs and updating the database.
    test_download_pdf_with_selenium: Tests the `download_pdf_with_selenium` 
        function to ensure that it navigates and interacts with a web page 
        as expected using the WebAutomationHelper.

Modules:
    - download_manager: Contains the `download_pdf_with_selenium`, 
      `load_config`, and `process_rows_for_download` functions for managing 
      downloads and database operations.

Example usage:
    pytest test_download_manager.py
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from download_manager import (download_pdf_with_selenium, load_config,
                              process_rows_for_download)


@pytest.fixture
def mock_db():
    """
    Fixture to mock the SQLite database connection and cursor.

    Returns:
        MagicMock: Mocked SQLite cursor object.
    """
    with patch("download_manager.sqlite3.connect") as mock_connect:
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        yield mock_cursor


@pytest.fixture
def mock_helper():
    """
    Fixture to mock the WebAutomationHelper class.

    Returns:
        MagicMock: Mocked WebAutomationHelper instance.
    """
    with patch("download_manager.WebAutomationHelper") as MockHelper:
        yield MockHelper.return_value


def test_load_config():
    """
    Test the `load_config` function to ensure it loads configuration from
    a JSON file correctly.

    Raises:
        AssertionError: If the loaded configuration does not match the
            expected values.
    """
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = (
            '{"url": "http://example.com"}'
        )
        config = load_config("config.json")
        assert config["url"] == "http://example.com"


def test_process_rows_for_download(mock_db):
    """
    Test the `process_rows_for_download` function to verify that it
    processes database rows correctly, including downloading PDFs and
    updating the database.

    Args:
        mock_db (MagicMock): Mocked SQLite cursor object.

    Raises:
        AssertionError: If the function does not commit changes to the
            database or process rows correctly.
    """
    mock_db.fetchall.return_value = [
        (1, "uuid1", "123456", "1001", "100.00", "2023-01-01"),
        (2, "uuid2", "654321", "1002", "200.00", "2023-02-01"),
    ]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_db

    with patch("download_manager.download_pdf_with_selenium") as mock_download, patch(
        "download_manager.shutil.move"
    ) as mock_move, patch("builtins.open", new_callable=MagicMock) as mock_open, patch(
        "download_manager.get_db_connection", return_value=(mock_conn, mock_db)
    ):

        mock_open.return_value.__enter__.return_value.read.return_value = b"PDF content"

        process_rows_for_download()

        mock_conn.commit.assert_called_once()


def test_download_pdf_with_selenium(mock_helper):
    """
    Test the `download_pdf_with_selenium` function to ensure it interacts
    with the web page as expected using the WebAutomationHelper.

    Args:
        mock_helper (MagicMock): Mocked WebAutomationHelper instance.

    Raises:
        AssertionError: If any of the expected interactions with the web
            page are not performed.
    """
    with patch(
        "download_manager.load_config",
        return_value={
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
        },
    ):
        download_pdf_with_selenium("123456", "1001", "100.00", "2023-01-01")

        mock_helper.navigate_to.assert_called_once()
        mock_helper.switch_to_frame.assert_any_call("initial_frame")
        mock_helper.input_data.assert_called_once_with(
            "123456", "1001", "100.00", "2023-01-01"
        )
        mock_helper.click_element.assert_any_call("search_button")
        mock_helper.switch_to_default_content.assert_called_once()
        mock_helper.switch_to_frame.assert_any_call("result_frame")
        mock_helper.switch_to_new_window.assert_called_once()
        mock_helper.click_element.assert_any_call("popup_download_button")
        mock_helper.close_window.assert_called_once()
        mock_helper.switch_to_main_window.assert_called_once()
        mock_helper.quit.assert_called_once()
