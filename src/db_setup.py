import sqlite3

def setup_database(db_path="check_recon.db"):
    """
    Sets up the database with the necessary tables for storing original data 
    and PDF data. Creates tables `original_data` and `pdf_data` if they do 
    not already exist.

    Args:
        db_path (str): The file path to the SQLite database. Defaults to 
            "check_recon.db".

    Returns:
        sqlite3.Connection: A connection object to the SQLite database.
    
    The `original_data` table contains the following fields:
        - id: Primary key, auto-incremented.
        - uuid: Unique identifier for each record.
        - acct_number: Account number related to the data.
        - check_number: Check number associated with the transaction.
        - amount: Transaction amount.
        - date: Transaction date.
        - payee: Payee of the transaction.
        - status: Status of the transaction, defaulting to 'pending'.

    The `pdf_data` table contains the following fields:
        - id: Primary key, auto-incremented.
        - original_data_id: Foreign key linking to the `original_data` table.
        - pdf_name: Name of the PDF file.
        - pdf_blob: Binary data of the PDF file.
        - pdf_file_path: File path of the stored PDF.

    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table to store original data with UUID or ID
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS original_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE,
        acct_number TEXT,
        check_number TEXT,
        amount TEXT,
        date TEXT,
        payee TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    # Table to store PDF data as BLOBs and file paths
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pdf_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_data_id INTEGER,
        pdf_name TEXT,
        pdf_blob BLOB,
        pdf_file_path TEXT,
        FOREIGN KEY(original_data_id) REFERENCES original_data(id)
    )
    """)

    conn.commit()
    return conn
