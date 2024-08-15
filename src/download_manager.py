"""
This module contains functions and classes for processing and managing PDF 
downloads, conversions, and storage in a database. The script is designed to 
automate the process of downloading PDFs, converting them to images, and 
storing both the PDFs and images as BLOBs in an SQLite database.

Functions:
    load_config(config_file):
        Load the configuration from a JSON file.

    get_db_connection(db_path):
        Get a connection to the SQLite database.

    process_rows_for_download(db_path="data/check_recon.db", download_directory="data/stored_pdfs"):
        Processes rows with a 'pending' status from the `original_data` table in
        the database. For each row, a PDF is downloaded using Selenium, stored as
        a BLOB in the database, and the corresponding file is saved in the
        specified directory.

    download_pdf_with_selenium(acct_number, check_number, amount, date, config_file="../config/config.json"):
        Automates the process of downloading a PDF using Selenium based on the
        provided account number, check number, amount, and date.

Modules:
    - selenium_helper: Contains the `WebAutomationHelper` class used for Selenium
      automation tasks.
    - pdf_converter: Contains the `PDFConverter` class used to convert PDF BLOBs
      into images.
    - image_storage: Contains the `ImageStorage` class used to store images as
      BLOBs in the database.

Example usage:
    process_rows_for_download("data/check_recon.db", "data/stored_pdfs")
"""

import json
import os
import shutil
import sqlite3

from pdf2image import convert_from_bytes

from image_storage import ImageStorage
from pdf_converter import PDFConverter
from selenium_helper import WebAutomationHelper


def load_config(config_file):
    """
    Load the configuration from a JSON file.

    Args:
        config_file (str): The path to the configuration JSON file.

    Returns:
        dict: The loaded configuration dictionary.
    """
    with open(config_file, "r") as file:
        return json.load(file)


def get_db_connection(db_path):
    """
    Get a connection to the SQLite database.

    Args:
        db_path (str): The file path to the SQLite database.

    Returns:
        tuple: A tuple containing the database connection and cursor.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    return conn, cursor


def process_rows_for_download(
    db_path="data/check_recon.db", download_directory="data/stored_pdfs"
):
    """
    Processes rows with a 'pending' status from the `original_data` table in
    the database. For each row, a PDF is downloaded using Selenium, stored as
    a BLOB in the database, and the corresponding file is saved in the
    specified directory.

    Args:
        db_path (str): The file path to the SQLite database. Defaults to
            "data/check_recon.db".
        download_directory (str): The directory where downloaded PDFs will be
            stored. Defaults to "data/stored_pdfs".

    Returns:
        None

    The function performs the following steps:
        1. Connects to the database and fetches rows with a 'pending' status.
        2. For each row, uses Selenium to download the PDF corresponding to
           the data in the row.
        3. Renames the downloaded PDF and moves it to the specified directory.
        4. Stores the PDF as a BLOB in the `pdf_data` table and updates the
           file path.
        5. Converts the PDF BLOB to images.
        6. Stores the images as BLOBs in the database.
        7. Updates the status of the original data to 'downloaded' or 'failed'
           in case of an error.

    Notes:
        The function assumes that `download_pdf_with_selenium` is properly
        implemented to handle the Selenium automation and file download.

    Raises:
        Any exceptions that occur during PDF download or file operations are
        caught and logged. The status of the affected row is updated to
        'failed' in the database.

    Example usage:
        process_rows_for_download("data/check_recon.db", "data/stored_pdfs")
    """
    # Setup the database connection
    conn, cursor = get_db_connection(db_path)

    # Ensure the download directory exists
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    # Fetch pending rows from the database
    cursor.execute("SELECT * FROM original_data WHERE status='pending'")
    rows = cursor.fetchall()

    for row in rows:
        original_data_id = row[0]
        uuid = row[1]
        acct_number = row[2]
        check_number = row[3]
        amount = row[4]
        date = row[5]

        try:
            # Use Selenium to download the PDF for this use case
            download_pdf_with_selenium(acct_number, check_number, amount, date)

            # Rename the file and move it to the target directory
            unique_pdf_name = f"{uuid}_{os.path.basename('data/temp/image.pdf')}"
            new_pdf_path = os.path.join(download_directory, unique_pdf_name)
            shutil.move("data/temp/image.pdf", new_pdf_path)

            # Store the PDF as a BLOB and save the file path in the database
            with open(new_pdf_path, "rb") as file:
                pdf_blob = file.read()

            cursor.execute(
                """INSERT INTO pdf_data (uuid, pdf_name, pdf_blob, pdf_file_path)
                VALUES (?, ?, ?, ?)""",
                (uuid, unique_pdf_name, pdf_blob, new_pdf_path),
            )
            pdf_data_id = cursor.lastrowid

            # Convert the PDF BLOB to images
            pdf_converter = PDFConverter(pdf_blob)
            images = pdf_converter.convert_to_images()

            # Store the images as BLOBs in the database
            image_storage = ImageStorage(db_path=db_path)
            for image in images:
                image_storage.save_image_blob(pdf_data_id, "processed", image)

            # Update the status of the original data to 'downloaded'
            cursor.execute(
                "UPDATE original_data SET status='downloaded' WHERE id=?",
                (original_data_id,),
            )

        except Exception as e:
            # Handle any exceptions, e.g., download failures
            print(f"Failed to download for row {original_data_id}: {e}")
            cursor.execute(
                "UPDATE original_data SET status='failed' WHERE id=?",
                (original_data_id,),
            )

    conn.commit()
    conn.close()


def download_pdf_with_selenium(
    acct_number, check_number, amount, date, config_file="../config/config.json"
):
    """
    Automates the process of downloading a PDF using Selenium based on the
    provided account number, check number, amount, and date.

    Args:
        acct_number (str): The account number to input in the form.
        check_number (str): The check number to input in the form.
        amount (str): The amount to input in the form.
        date (str): The date to input in the form.

    Returns:
        str: The file path to the downloaded PDF.

    Raises:
        Exception: If any errors occur during the download process.

    Notes:
        The function assumes the existence of a `WebAutomationHelper` class
        that manages the Selenium WebDriver operations, including navigating
        to the necessary pages, inputting data, and handling the download.
    """
    # Initialize the Selenium WebAutomationHelper class with appropriate config
    config = load_config(config_file)
    helper = WebAutomationHelper(config=config)

    # Navigate to the initial page
    helper.navigate_to()

    # Input the necessary data (excluding Payee as per your instruction)
    helper.switch_to_frame("initial_frame")
    helper.input_data(acct_number, check_number, amount, date)
    helper.click_element("search_button")

    # Download the PDF
    helper.switch_to_default_content()
    helper.switch_to_frame("result_frame")
    # pdf_path = helper.download_file(uuid)  # This function handles the file download and renaming

    # Handle any pop-ups for finalizing the download
    helper.switch_to_new_window()
    helper.click_element("popup_download_button")

    # Close the pop-up and return to the main window
    helper.close_window()
    helper.switch_to_main_window()

    helper.quit()
