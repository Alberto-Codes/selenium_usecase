from typing import List

import duckdb
import pandas as pd


def initialize_connection(db_path: str) -> duckdb.DuckDBPyConnection:
    """Initializes a connection to the DuckDB database.

    Args:
        db_path (str): Path to the DuckDB database file.

    Returns:
        duckdb.DuckDBPyConnection: A connection object to interact with the
        database.

    Raises:
        ConnectionError: If the connection to the database fails.
    """
    try:
        return duckdb.connect(database=db_path, read_only=True)
    except duckdb.Error as e:
        raise ConnectionError(f"Failed to connect to database: {e}")


def fetch_tables(con: duckdb.DuckDBPyConnection) -> List[str]:
    """Fetches the list of table names from the database.

    Args:
        con (duckdb.DuckDBPyConnection): The database connection object.

    Returns:
        List[str]: A list of table names available in the database.

    Raises:
        ValueError: If fetching tables fails.
    """
    try:
        return con.execute("SHOW TABLES").fetchdf()["name"].tolist()
    except duckdb.Error as e:
        raise ValueError(f"Failed to fetch tables: {e}")


def fetch_columns(con: duckdb.DuckDBPyConnection, table_name: str) -> List[str]:
    """Fetches the list of column names for a selected table.

    Args:
        con (duckdb.DuckDBPyConnection): The database connection object.
        table_name (str): The name of the table to fetch columns from.

    Returns:
        List[str]: A list of column names for the selected table.

    Raises:
        ValueError: If fetching columns fails.
    """
    try:
        return con.execute(f"DESCRIBE {table_name}").fetchdf()["name"].tolist()
    except duckdb.Error as e:
        raise ValueError(f"Failed to fetch columns for table {table_name}: {e}")


def fetch_data(con: duckdb.DuckDBPyConnection, query: str) -> pd.DataFrame:
    """Executes the given SQL query and fetches the result as a DataFrame.

    Args:
        con (duckdb.DuckDBPyConnection): The database connection object.
        query (str): The SQL query to execute.

    Returns:
        pd.DataFrame: The query result as a pandas DataFrame.

    Raises:
        ValueError: If query execution fails.
    """
    try:
        return con.execute(query).fetchdf()
    except duckdb.Error as e:
        raise ValueError(f"Failed to execute query: {e}")
