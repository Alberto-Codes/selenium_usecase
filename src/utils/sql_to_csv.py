import duckdb
import pandas as pd


class SQLToCSVExporter:
    """
    A class to execute SQL queries from a file and export the results to a CSV file.

    Attributes:
        db_path (str): The path to the DuckDB database file.

    Methods:
        run_query_from_file_and_export(sql_file_path, output_csv_path):
            Execute an SQL query from a file and export the results to a CSV file.
    """

    def __init__(self, db_path="use_cases.duckdb"):
        """
        Initialize the SQLToCSVExporter with the path to the DuckDB database.

        Args:
            db_path (str): The path to the DuckDB database file. Defaults to
                "use_cases.duckdb".
        """
        self.db_path = db_path

    def run_query_from_file_and_export(self, sql_file_path, output_csv_path):
        """
        Execute an SQL query from a file and export the results to a CSV file.

        Args:
            sql_file_path (str): The file path to the SQL file containing the query.
            output_csv_path (str): The file path where the CSV file will be saved.

        Raises:
            Exception: If an error occurs during query execution or file export.

        Example usage:
            exporter = SQLToCSVExporter(db_path="use_cases.duckdb")
            exporter.run_query_from_file_and_export("src/SQL/sel.sql", "output/query_results.csv")
        """
        try:
            # Read the SQL query from the file
            with open(sql_file_path, "r") as file:
                query = file.read()

            # Connect to the DuckDB database
            conn = duckdb.connect(self.db_path)

            # Execute the SQL query and fetch the results into a Pandas DataFrame
            df = conn.execute(query).df()

            # Export the DataFrame to a CSV file
            df.to_csv(output_csv_path, index=False)

            print(f"Exported {len(df)} records to {output_csv_path}")

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            # Ensure the connection is closed
            conn.close()


# Example usage:
if __name__ == "__main__":
    db_path = "use_cases.duckdb"
    sql_file_path = "src/SQL/sel.sql"
    output_csv_path = "data/output/query_results.csv"

    exporter = SQLToCSVExporter(db_path=db_path)
    exporter.run_query_from_file_and_export(sql_file_path, output_csv_path)
