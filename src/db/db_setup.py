"""
This module defines the ORM (Object-Relational Mapping) models and utility 
functions for setting up and managing a database using SQLAlchemy. The 
database is used to track records, PDF files, images, OCR results, and batch 
processing statuses.

Classes:
    TblRCNInput: Represents the input table for records, tracking basic 
        details like account number, check number, amount, payee, and status.
    TblRCNPDF: Represents the table for storing PDF files as BLOBs linked to 
        the input table.
    TblRCNImage: Represents the table for storing images as BLOBs, linked to 
        the input table and optionally to a PDF.
    TblRCNOCRResult: Represents the table for storing OCR results, linked to 
        images.
    TblRCNBatchStatus: Represents the table for tracking the status of batch 
        processing operations.

Functions:
    generate_uuid(): Generates a unique UUID string.
    create_database(db_path='data/rcn.db', echo=False): Creates the database 
        and the tables defined in this module.
    destroy_database(db_path='data/rcn.db'): Destroys the database by deleting 
        the file.
    get_session(engine): Sets up and returns a new SQLAlchemy session bound to 
        the provided engine.

Example usage:
    # Create the database and get a session
    engine = create_database(db_path='data/rcn.db', echo=True)
    session = get_session(engine)

    # Destroy the database (for debugging purposes)
    destroy_database(db_path='data/rcn.db')
"""

import uuid

import duckdb
from sqlalchemy import (Column, Date, Float, ForeignKey, Integer, LargeBinary,
                        String, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def generate_uuid():
    """
    Generates a unique UUID string.

    Returns:
        str: A unique UUID string.
    """
    return str(uuid.uuid4())


class TblRCNInput(Base):
    """
    Represents the input table for records, tracking basic details like account
    number, check number, amount, payee, and status.

    Attributes:
        id (str): Primary key, unique identifier for each record.
        guid (str): Unique GUID for each record.
        account_number (str): Account number associated with the record.
        check_number (str): Check number associated with the record.
        amount (float): Amount associated with the record.
        payee (str): Payee associated with the record.
        issue_date (Date): Date the check was issued.
        batch_uuid (str): Foreign key linking to a batch record.
        status (str): Status of the record (e.g., 'pending', 'processed').
    """

    __tablename__ = "tbl_RCN_Input"

    id = Column(String, primary_key=True, default=generate_uuid)
    guid = Column(String, unique=True, nullable=False)
    account_number = Column(String)
    check_number = Column(String)
    amount = Column(Float)
    payee = Column(String)
    issue_date = Column(Date)
    batch_uuid = Column(String, ForeignKey("tbl_RCN_Batch.id"), nullable=True)
    status = Column(String, default="pending")


class TblRCNPDF(Base):
    """
    Represents the table for storing PDF files as BLOBs linked to the input
    table.

    Attributes:
        id (str): Primary key, unique identifier for each PDF.
        input_table_id (str): Foreign key linking to the input table.
        pdf_blob (LargeBinary): BLOB storage for the PDF file.
    """

    __tablename__ = "tbl_RCN_PDF"

    id = Column(String, primary_key=True, default=generate_uuid)
    input_table_id = Column(String, ForeignKey("tbl_RCN_Input.id"), nullable=False)
    pdf_blob = Column(LargeBinary)


class TblRCNImage(Base):
    """
    Represents the table for storing images as BLOBs, linked to the input
    table and optionally to a PDF.

    Attributes:
        id (str): Primary key, unique identifier for each image.
        input_table_id (str): Foreign key linking to the input table.
        pdf_id (str): Foreign key linking to a PDF record, if the image was
            generated from a PDF.
        image_blob (LargeBinary): BLOB storage for the image file.
    """

    __tablename__ = "tbl_RCN_Image"

    id = Column(String, primary_key=True, default=generate_uuid)
    input_table_id = Column(String, ForeignKey("tbl_RCN_Input.id"), nullable=False)
    pdf_id = Column(String, ForeignKey("tbl_RCN_PDF.id"), nullable=True)
    image_blob = Column(LargeBinary)


class TblRCNOCRResult(Base):
    """
    Represents the table for storing OCR results, linked to images.

    Attributes:
        id (str): Primary key, unique identifier for each OCR result.
        image_id (str): Foreign key linking to the image table.
        preprocessing_type (str): The type of preprocessing applied before OCR.
        extracted_text (str): The text extracted from the image.
        payee_match (str): Indicator of whether the extracted text matches
            the expected payee.
    """

    __tablename__ = "tbl_RCN_OCR"

    id = Column(String, primary_key=True, default=generate_uuid)
    image_id = Column(String, ForeignKey("tbl_RCN_Image.id"), nullable=False)
    preprocessing_type = Column(String)
    extracted_text = Column(String)
    payee_match = Column(String)


class TblRCNBatchStatus(Base):
    """
    Represents the table for tracking the status of batch processing
    operations.

    Attributes:
        id (str): Primary key, autoincrementing identifier for each batch
            status.
        batch_id (str): Unique identifier for the batch.
        status (str): Status of the batch (e.g., 'pending', 'completed').
        failed_records (int): Number of records in the batch that failed to
            process.
    """

    __tablename__ = "tbl_RCN_Batch"

    id = Column(String, primary_key=True, default=generate_uuid)
    status = Column(String, default="pending")
    failed_records = Column(Integer, default=0)


def create_database(db_path="data/rcn.db", echo=False):
    """
    Creates the database and the tables defined in this module.

    Args:
        db_path (str): The path where the database file will be created.
            Defaults to 'data/rcn.db'.
        echo (bool): If True, SQLAlchemy will log all the SQL statements.
            Defaults to False.

    Returns:
        sqlalchemy.engine.base.Engine: The SQLAlchemy engine connected to the
        database.
    """
    engine = create_engine(f"duckdb:///{db_path}", echo=echo)
    Base.metadata.create_all(engine)
    return engine


def destroy_database(db_path="data/rcn.db"):
    """
    Destroys the database by deleting the file.

    Args:
        db_path (str): The path where the database file is located.
            Defaults to 'data/rcn.db'.
    """
    import os

    if os.path.exists(db_path):
        os.remove(db_path)


def get_session(engine):
    """
    Sets up and returns a new SQLAlchemy session bound to the provided engine.

    Args:
        engine (sqlalchemy.engine.base.Engine): The SQLAlchemy engine connected
            to the database.

    Returns:
        sqlalchemy.orm.session.Session: A new session object for database
        operations.
    """
    Session = sessionmaker(bind=engine)
    return Session()
