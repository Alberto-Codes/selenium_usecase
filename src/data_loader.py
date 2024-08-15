import uuid

import pandas as pd

from db_setup import setup_database


def load_dataset_into_db(spreadsheet_path, db_path="use_cases.db"):
    """
    Loads data from a spreadsheet into the database, adding a UUID to each
    record before insertion. The function creates the necessary tables if
    they do not already exist.

    Args:
        spreadsheet_path (str): The file path to the spreadsheet containing
            the data to be loaded.
        db_path (str): The file path to the SQLite database. Defaults to
            "use_cases.db".

    Returns:
        None

    The function performs the following steps:
        1. Loads the spreadsheet into a pandas DataFrame.
        2. Generates a unique UUID for each row in the DataFrame.
        3. Sets up the SQLite database and creates tables if they do not
           already exist.
        4. Inserts the data from the DataFrame into the `original_data` table
           in the database.
    """
    # Load the spreadsheet
    df = pd.read_excel(spreadsheet_path)

    # Add UUIDs to the dataframe
    df["uuid"] = [str(uuid.uuid4()) for _ in range(len(df))]

    # Setup the database
    conn = setup_database(db_path)

    # Insert original data into the database
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute(
            """
        INSERT INTO original_data (uuid, acct_number, check_number, amount, date, payee)
        VALUES (?, ?, ?, ?, ?, ?)""",
            (
                row["uuid"],
                row["AcctNumber"],
                row["CheckNumber"],
                row["Amount"],
                row["Date"],
                row["Payee"],
            ),
        )

    conn.commit()
    conn.close()
