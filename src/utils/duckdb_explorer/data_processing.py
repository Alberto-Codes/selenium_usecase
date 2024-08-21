from typing import List, Optional

import pandas as pd


def construct_query(
    selected_columns: List[str], table_name: str, where_clause: Optional[str] = None
) -> str:
    """Constructs an SQL query to fetch data based on selected columns and table.

    Args:
        selected_columns (List[str]): List of columns to include in the query.
        table_name (str): Name of the table to query.
        where_clause (Optional[str]): Optional SQL WHERE clause to filter results.
            Defaults to None.

    Returns:
        str: The constructed SQL query.
    """
    query = f"SELECT {', '.join(selected_columns)} FROM {table_name}"
    if where_clause:
        query += f" WHERE {where_clause}"
    return query


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Converts a pandas DataFrame to CSV format.

    Args:
        df (pd.DataFrame): The DataFrame to convert.

    Returns:
        bytes: The CSV data encoded as bytes.
    """
    return df.to_csv().encode("utf-8")
