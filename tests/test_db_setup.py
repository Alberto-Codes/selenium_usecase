"""
This module contains unit tests for the database setup and ORM models defined 
in the `db_setup.py` module. The tests verify the creation, destruction, and 
basic CRUD operations on the database tables using SQLAlchemy with a DuckDB 
database engine.

Fixtures:
    engine: Provides a DuckDB database engine for testing purposes. It creates 
        a temporary in-memory database for testing and ensures cleanup after 
        tests are complete.
    session: Provides a SQLAlchemy session bound to the DuckDB database engine 
        for database operations during testing.

Tests:
    test_create_database(engine): Verifies that the database and tables are 
        created successfully by checking the existence of each table.
    test_destroy_database(): Ensures that the database file is destroyed successfully.
    test_get_session(engine): Confirms that a new SQLAlchemy session is created 
        successfully.
    test_tbl_rcn_input(session): Verifies that records can be inserted into the 
        `TblRCNInput` table.
    test_tbl_rcn_pdf(session): Verifies that records can be inserted into the 
        `TblRCNPDF` table, with appropriate foreign key relationships.
    test_tbl_rcn_image(session): Verifies that records can be inserted into the 
        `TblRCNImage` table, with appropriate foreign key relationships.
    test_tbl_rcn_ocr_result(session): Verifies that records can be inserted into 
        the `TblRCNOCRResult` table, with appropriate foreign key relationships.
    test_tbl_rcn_batch_status(session): Verifies that records can be inserted into 
        the `TblRCNBatchStatus` table.

Example usage:
    pytest test_db_setup.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from db.db_setup import (TblRCNBatchStatus, TblRCNImage, TblRCNInput,
                         TblRCNOCRResult, TblRCNPDF, create_database,
                         destroy_database, get_session)


@pytest.fixture(scope="module")
def engine():
    """
    Fixture to create a DuckDB database engine for testing.

    Returns:
        sqlalchemy.engine.base.Engine: The SQLAlchemy engine connected to the DuckDB database.
    """
    db_path = "test_rcn.db"
    engine = create_engine(f"duckdb:///{db_path}", echo=True)
    create_database(db_path=db_path)
    yield engine
    destroy_database(db_path)


@pytest.fixture(scope="module")
def session(engine):
    """
    Fixture to create a SQLAlchemy session for testing.

    Returns:
        sqlalchemy.orm.session.Session: A new session object for database operations.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_database(engine):
    """
    Test that the database and tables are created successfully.
    """
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_name = 'tbl_RCN_Input'"
            )
        )
        assert result.fetchone() is not None

        result = connection.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_name = 'tbl_RCN_PDF'"
            )
        )
        assert result.fetchone() is not None

        result = connection.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_name = 'tbl_RCN_Image'"
            )
        )
        assert result.fetchone() is not None

        result = connection.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_name = 'tbl_RCN_OCR'"
            )
        )
        assert result.fetchone() is not None

        result = connection.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_name = 'tbl_RCN_Batch'"
            )
        )
        assert result.fetchone() is not None


def test_destroy_database():
    """
    Test that the database file is destroyed successfully.

    Raises:
        AssertionError: If the database file is not deleted.
    """
    db_path = "test_rcn.db"
    create_database(db_path)
    destroy_database(db_path)
    assert not os.path.exists(db_path)


def test_get_session(engine):
    """
    Test that a new SQLAlchemy session is created successfully.

    Args:
        engine (sqlalchemy.engine.base.Engine): The SQLAlchemy engine connected to the database.
    """
    session = get_session(engine)
    assert session is not None
    session.close()


def test_tbl_rcn_input(session):
    """
    Test that records can be inserted into the TblRCNInput table.

    Args:
        session (sqlalchemy.orm.session.Session): The SQLAlchemy session for database operations.
    """
    record = TblRCNInput(
        guid="test-guid",
        account_number="123456",
        check_number="7890",
        amount=100.0,
        payee="Test Payee",
        issue_date="2023-01-01",
        status="pending",
    )
    session.add(record)
    session.commit()
    assert session.query(TblRCNInput).filter_by(guid="test-guid").first() is not None


def test_tbl_rcn_pdf(session):
    """
    Test that records can be inserted into the TblRCNPDF table.

    Args:
        session (sqlalchemy.orm.session.Session): The SQLAlchemy session for database operations.
    """
    # Insert a record into the TblRCNInput table to satisfy the foreign key constraint
    input_record = TblRCNInput(
        guid="pdf-test-guid",
        account_number="654321",
        check_number="0987",
        amount=200.0,
        payee="Test Payee PDF",
        issue_date="2023-01-02",
        status="pending",
    )
    session.add(input_record)
    session.commit()

    pdf = TblRCNPDF(input_table_id=input_record.id, pdf_blob=b"test-pdf-blob")
    session.add(pdf)
    session.commit()
    assert (
        session.query(TblRCNPDF).filter_by(input_table_id=input_record.id).first()
        is not None
    )


def test_tbl_rcn_image(session):
    """
    Test that records can be inserted into the TblRCNImage table.

    Args:
        session (sqlalchemy.orm.session.Session): The SQLAlchemy session for database operations.
    """
    # Insert a record into the TblRCNInput table to satisfy the foreign key constraint
    input_record = TblRCNInput(
        guid="image-test-guid",
        account_number="111222",
        check_number="3333",
        amount=300.0,
        payee="Test Payee Image",
        issue_date="2023-01-03",
        status="pending",
    )
    session.add(input_record)
    session.commit()

    image = TblRCNImage(
        input_table_id=input_record.id,
        image_blob=b"test-image-blob",
    )
    session.add(image)
    session.commit()
    assert (
        session.query(TblRCNImage).filter_by(input_table_id=input_record.id).first()
        is not None
    )


def test_tbl_rcn_ocr_result(session):
    """
    Test that records can be inserted into the TblRCNOCRResult table.

    Args:
        session (sqlalchemy.orm.session.Session): The SQLAlchemy session for database operations.
    """
    # Insert a record into the TblRCNInput and TblRCNImage tables to satisfy the foreign key constraint
    input_record = TblRCNInput(
        guid="ocr-test-guid",
        account_number="444555",
        check_number="6666",
        amount=400.0,
        payee="Test Payee OCR",
        issue_date="2023-01-04",
        status="pending",
    )
    session.add(input_record)
    session.commit()

    image = TblRCNImage(
        input_table_id=input_record.id,
        image_blob=b"test-image-blob",
    )
    session.add(image)
    session.commit()

    ocr_result = TblRCNOCRResult(
        image_id=image.id,
        preprocessing_type="test-preprocessing",
        extracted_text="test-text",
        payee_match="yes",
    )
    session.add(ocr_result)
    session.commit()
    assert (
        session.query(TblRCNOCRResult).filter_by(image_id=image.id).first() is not None
    )


def test_tbl_rcn_batch_status(session):
    """
    Test that records can be inserted into the TblRCNBatchStatus table.

    Args:
        session (sqlalchemy.orm.session.Session): The SQLAlchemy session for database operations.
    """
    batch_status = TblRCNBatchStatus(
        id="test-batch-id", status="pending", failed_records=0
    )
    session.add(batch_status)
    session.commit()
    assert (
        session.query(TblRCNBatchStatus).filter_by(id="test-batch-id").first()
        is not None
    )
