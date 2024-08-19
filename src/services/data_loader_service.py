import uuid
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from src.db.models.input import TblRCNInput


class DataLoaderService:
    """
    Service class responsible for loading data from a spreadsheet into the input table.
    """

    def __init__(self, session: Session):
        """
        Initializes the DataLoaderService with a SQLAlchemy session.

        Args:
            session (Session): The SQLAlchemy session for database operations.
        """
        self.session = session

    def load_dataset_into_db(self, spreadsheet_path: str) -> None:
        """
        Loads data from a spreadsheet into the input table, adding a UUID to each record.

        Args:
            spreadsheet_path (str): The file path to the spreadsheet containing the data to be loaded.

        Returns:
            None
        """
        # Load the spreadsheet into a DataFrame
        df = pd.read_excel(spreadsheet_path)

        # Add UUIDs to the dataframe
        df["uuid"] = [str(uuid.uuid4()) for _ in range(len(df))]

        # Insert data into the input table
        for _, row in df.iterrows():
            record = TblRCNInput(
                id=row["uuid"],
                guid=row["uuid"],
                account_number=row["AcctNumber"],
                check_number=row["CheckNumber"],
                amount=row["Amount"],
                issue_date=row["Date"],
                payee=row["Payee"],
                status="pending",  # Set default status
            )
            self.session.add(record)

        # Commit the transaction
        self.session.commit()
