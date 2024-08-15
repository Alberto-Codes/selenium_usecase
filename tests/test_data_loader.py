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
    # Create a temporary spreadsheet
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
    # Create a temporary database
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
