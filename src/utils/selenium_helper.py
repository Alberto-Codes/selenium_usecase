import os
import shutil
from sqlalchemy.orm import Session
from sqlalchemy import update
from src.db.models import TblRCNInput, TblRCNPDF
from src.selenium_helper import WebAutomationHelper

def process_rows_for_download(session: Session, download_directory: str = "data/PDFs"):
    """
    Processes rows with a 'pending' status from the `TblRCNInput` table in the database.
    For each row, a PDF is downloaded using Selenium, stored as a BLOB in the `TblRCNPDF` table,
    and the corresponding file is saved in the specified directory.

    Args:
        session (Session): The SQLAlchemy session for database operations.
        download_directory (str): The directory where downloaded PDFs will be stored. Defaults to "data/PDFs".

    Returns:
        None
    """
    # Ensure the download directory exists
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    # Ensure the temporary download directory exists
    temp_directory = "data/tmp/"
    if not os.path.exists(temp_directory):
        os.makedirs(temp_directory)

    # Fetch pending rows from the database
    pending_rows = session.query(TblRCNInput).filter(TblRCNInput.status == 'pending').limit(10).all()

    for row in pending_rows:
        try:
            # Use Selenium to download the PDF for this use case
            download_pdf_with_selenium(row.account_number, row.check_number, row.amount, row.issue_date)

            # Read the downloaded PDF
            temp_pdf_path = os.path.join(temp_directory, "Image.pdf")
            with open(temp_pdf_path, "rb") as file:
                pdf_blob = file.read()

            # Save the PDF as a BLOB in the TblRCNPDF table
            pdf_record = TblRCNPDF(input_table_id=row.id, pdf_blob=pdf_blob)
            session.add(pdf_record)
            session.commit()

            # Move the PDF file to the final directory with a unique name based on the PDF table's ID
            pdf_id = pdf_record.id
            pdf_filename = f"{pdf_id}.pdf"
            new_pdf_path = os.path.join(download_directory, pdf_filename)
            shutil.move(temp_pdf_path, new_pdf_path)

            # Update the status of the original data to 'downloaded'
            stmt = update(TblRCNInput).where(TblRCNInput.id == row.id).values(status='downloaded')
            session.execute(stmt)

        except Exception as e:
            # Handle any exceptions, e.g., download failures
            print(f"Failed to download for row {row.id}: {e}")
            session.rollback()  # Rollback in case of failure
            stmt = update(TblRCNInput).where(TblRCNInput.id == row.id).values(status='failed')
            session.execute(stmt)

        finally:
            session.commit()

def download_pdf_with_selenium(acct_number, check_number, amount, date):
    """
    Automates the process of downloading a PDF using Selenium based on the provided account number, check number, amount, and date.
    
    The PDF is always downloaded to 'data/tmp/Image.pdf'.
    
    Args:
        acct_number (str): The account number to input in the form.
        check_number (str): The check number to input in the form.
        amount (str): The amount to input in the form.
        date (str): The date to input in the form.
        
    Returns:
        None
    """
    # Initialize the Selenium WebAutomationHelper class
    helper = WebAutomationHelper()

    # Perform the necessary steps to download the PDF
    helper.navigate_to()
    helper.input_data(acct_number, check_number, amount, date)
    
    # Specify the download directory and file name
    temp_pdf_path = os.path.join("data/tmp/", "Image.pdf")
    
    # Download the PDF and save it to the temp directory
    helper.download_pdf(temp_pdf_path)

    helper.quit()
