"""
This script contains unit tests for verifying the correct setup of the 
SQLite database using the pytest framework. The tests ensure that the 
database and necessary tables are created as expected.

Fixtures:
    db_connection: Creates a connection to a temporary SQLite database for 
        testing. Ensures that the database is cleaned up after tests are 
        complete.

Tests:
    test_database_creation: Verifies that the SQLite database file is 
        created successfully.
    test_tables_creation: Checks that the required tables (`original_data`, 
        `pdf_data`, and `ocr_images`) are created in the database.

Modules:
    - db_setup: Contains the `setup_database` function used to initialize 
      the database.

Example usage:
    pytest test_db_setup.py
"""

import os
import sys
import sqlite3
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from db_setup import setup_database

@pytest.fixture(scope="module")
def db_connection():
    """
    Fixture to create a connection to a temporary SQLite database.

    Returns:
        sqlite3.Connection: A connection object to the temporary database.
    """
    test_db_path = "test_check_recon.db"
    conn = setup_database(test_db_path)
    yield conn
    conn.close()
    os.remove(test_db_path)

def test_database_creation(db_connection):
    """
    Test that the SQLite database file is created.

    Args:
        db_connection (sqlite3.Connection): The database connection fixture.

    Raises:
        AssertionError: If the database file does not exist.
    """
    assert os.path.exists("test_check_recon.db")

def test_tables_creation(db_connection):
    """
    Test that the required tables are created in the database.

    Args:
        db_connection (sqlite3.Connection): The database connection fixture.

    Raises:
        AssertionError: If the `original_data`, `pdf_data`, or `ocr_images` tables are not
            found in the database.
    """
    cursor = db_connection.cursor()

    # Check if original_data table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='original_data'"
    )
    assert cursor.fetchone() is not None

    # Check if pdf_data table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='pdf_data'"
    )
    assert cursor.fetchone() is not None

    # Check if ocr_images table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='ocr_images'"
    )
    assert cursor.fetchone() is not None
