"""
This script contains unit tests for the `load_dataset_into_db` function
and the `setup_database` function using the pytest framework. The tests
verify that the functions work correctly by creating temporary
spreadsheets and databases, loading data into the database, and
validating the results.

Fixtures:
    temp_spreadsheet: Creates a temporary Excel spreadsheet with sample
        data for testing.
    temp_db: Creates a temporary SQLite database for testing.

Tests:
    test_load_dataset_into_db: Tests the `load_dataset_into_db` function
        by verifying that the data is correctly loaded into the database
        and the table contents match the expected values.

Modules:
    - data_loader: Contains the `load_dataset_into_db` function.
    - db_setup: Contains the `setup_database` function.

Example usage:
    pytest test_data_loader.py
"""

import os
import sqlite3
import sys

import pandas as pd
import pytest

# Ensure the src directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from data_loader import load_dataset_into_db
from db_setup import setup_database


@pytest.fixture(scope="module")
def temp_spreadsheet():
    """
    Fixture to create a temporary spreadsheet with sample data.

    Returns:
        str: Path to the temporary spreadsheet file.
    """
    temp_spreadsheet_path = "temp_spreadsheet.xlsx"
    df = pd.DataFrame(
        {
            "uuid": [
                "7de604a6-0750-453f-b121-478b38f9b1f4",
                "d7b264e5-d5c6-41a6-ae4e-5b6b1e1b1f4e",
            ],
            "AcctNumber": ["123456", "789012"],
            "CheckNumber": ["1001", "1002"],
            "Amount": ["100.00", "200.00"],
            "Date": ["2023-01-01", "2023-01-02"],
            "Payee": ["John Doe", "Jane Doe"],
        }
    )
    df.to_excel(temp_spreadsheet_path, index=False)
    yield temp_spreadsheet_path
    os.remove(temp_spreadsheet_path)


@pytest.fixture(scope="module")
def temp_db():
    """
    Fixture to create a temporary SQLite database.

    Returns:
        str: Path to the temporary database file.
    """
    temp_db_path = "temp_use_cases.db"
    conn = setup_database(temp_db_path)
    conn.close()
    yield temp_db_path
    # Ensure the database connection is closed before removing the file
    try:
        os.remove(temp_db_path)
    except PermissionError:
        pass


def test_load_dataset_into_db(temp_spreadsheet, temp_db):
    """
    Test the `load_dataset_into_db` function.

    This test loads data from a temporary spreadsheet into a temporary
    database and verifies that the data is correctly inserted into the
    `original_data` table.

    Args:
        temp_spreadsheet (str): Path to the temporary spreadsheet.
        temp_db (str): Path to the temporary database.

    Raises:
        AssertionError: If the data in the database does not match the
            expected values.
    """
    # Call the function to load data into the database
    load_dataset_into_db(temp_spreadsheet, temp_db)

    # Verify the data in the database
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    # Clean up the table before running the test
    cursor.execute("DELETE FROM original_data")
    conn.commit()
    conn.close()

    # Call the function to load data into the database again
    load_dataset_into_db(temp_spreadsheet, temp_db)

    # Check if data is inserted into original_data table
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM original_data")
    rows = cursor.fetchall()
    assert len(rows) == 2  # We inserted 2 rows

    # Verify the content of the first row
    assert rows[0][2] == "123456"  # AcctNumber
    assert rows[0][3] == "1001"  # CheckNumber
    assert float(rows[0][4]) == 100.00  # Amount
    assert rows[0][5] == "2023-01-01"  # Date
    assert rows[0][6] == "John Doe"  # Payee

    conn.close()
