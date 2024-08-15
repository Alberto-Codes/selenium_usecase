import duckdb
import cv2
import numpy as np
import io

class RecordInspector:
    """
    A class to inspect records from a DuckDB database, specifically focusing on 
    displaying images stored as BLOBs.

    Attributes:
        db_path (str): The path to the DuckDB database file.
        table_name (str): The name of the table from which to fetch records.
        conn (duckdb.DuckDBPyConnection): The connection object to the DuckDB database.
        batch_size (int): The number of records to fetch in each batch.
        offset (int): The offset for fetching records, used to navigate through 
            batches.

    Methods:
        fetch_records(): Fetch a batch of records from the database.
        display_records(records): Display records and their associated images.
        next_batch(): Fetch and display the next batch of records.
        previous_batch(): Fetch and display the previous batch of records.
        close(): Close the database connection.
    """

    def __init__(self, db_path="use_cases.duckdb", table_name="ocr_images"):
        """
        Initialize the RecordInspector with the database path and table name.

        Args:
            db_path (str): The path to the DuckDB database file. Defaults to 
                "use_cases.duckdb".
            table_name (str): The name of the table from which to fetch records. 
                Defaults to "ocr_images".
        """
        self.db_path = db_path
        self.table_name = table_name
        self.conn = duckdb.connect(self.db_path)
        self.batch_size = 10
        self.offset = 0

    def fetch_records(self):
        """
        Fetch a batch of records from the database.

        Returns:
            list: A list of tuples, each containing the record ID, PDF data ID, 
                processing type, and image BLOB.
        """
        query = f"""
        SELECT id, pdf_data_id, processing_type, image_blob 
        FROM {self.table_name} 
        LIMIT {self.batch_size} 
        OFFSET {self.offset}
        """
        records = self.conn.execute(query).fetchall()
        return records

    def display_records(self, records):
        """
        Display records and their associated images.

        Args:
            records (list): A list of tuples, each containing the record ID, 
                PDF data ID, processing type, and image BLOB.

        Notes:
            The images are displayed using OpenCV's imshow function. Press any 
            key to close the image display window.
        """
        for record in records:
            record_id, pdf_data_id, processing_type, image_blob = record
            print(f"Record ID: {record_id}, PDF Data ID: {pdf_data_id}, Processing Type: {processing_type}")

            # Convert the BLOB back to an image
            image_array = np.frombuffer(image_blob, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            # Display the image with its processing type
            cv2.imshow(f"Image - {processing_type}", image)
            cv2.waitKey(0)
        cv2.destroyAllWindows()

    def next_batch(self):
        """
        Fetch and display the next batch of records.

        If there are no more records, a message is displayed.
        """
        records = self.fetch_records()
        if records:
            self.display_records(records)
            self.offset += self.batch_size
        else:
            print("No more records to display.")

    def previous_batch(self):
        """
        Fetch and display the previous batch of records.

        If already at the first batch, a message is displayed.
        """
        if self.offset > 0:
            self.offset -= self.batch_size
            records = self.fetch_records()
            self.display_records(records)
        else:
            print("This is the first batch.")

    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()

# Example usage:
if __name__ == "__main__":
    inspector = RecordInspector(db_path="use_cases.duckdb")

    while True:
        command = input("Enter 'n' for next batch, 'p' for previous batch, 'q' to quit: ").strip().lower()

        if command == 'n':
            inspector.next_batch()
        elif command == 'p':
            inspector.previous_batch()
        elif command == 'q':
            inspector.close()
            break
        else:
            print("Invalid command. Please enter 'n', 'p', or 'q'.")
