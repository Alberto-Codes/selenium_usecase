import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import sqlite3

import pytest

from db_setup import setup_database


@pytest.fixture(scope="module")
def db_connection():
    test_db_path = "test_check_recon.db"
    conn = setup_database(test_db_path)
    yield conn
    conn.close()
    os.remove(test_db_path)


def test_database_creation(db_connection):
    assert os.path.exists("test_check_recon.db")


def test_tables_creation(db_connection):
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
