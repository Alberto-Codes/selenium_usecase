import csv
import os
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from src.db.db_setup import (TblRCNImage, TblRCNInput, TblRCNOCRResult,
                             TblRCNPDF, get_session)


def fetch_records_for_export(session: Session):
    """
    Fetch records where the sum of payee_match is 0 across all OCR results and the input status is 'payee_match_attempted'.
    """
    # Correcting the query structure
    records = (
        session.query(TblRCNInput)
        .join(TblRCNImage, TblRCNInput.id == TblRCNImage.input_table_id)
        .join(TblRCNPDF, TblRCNImage.pdf_id == TblRCNPDF.id)
        .join(TblRCNOCRResult, TblRCNImage.id == TblRCNOCRResult.image_id)
        .options(
            joinedload(TblRCNInput.images).joinedload(
                TblRCNImage.pdf
            ),  # eager load images and pdfs
            joinedload(TblRCNInput.images).joinedload(
                TblRCNImage.ocr_results
            ),  # eager load ocr_results
        )
        .filter(TblRCNInput.status == "payee_match_attempted")
        .group_by(TblRCNInput.id)
        .having(func.sum(TblRCNOCRResult.payee_match) == 0)
        .all()
    )
    return records


def export_to_csv(records, batch_id):
    """
    Export the fetched records to a CSV file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/output/payee_mismatch_{batch_id}_{timestamp}.csv"

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Input ID",
                "Batch ID",
                "Account Number",
                "Check Number",
                "Amount",
                "Payee 1",
                "Payee 2",
                "Issue Date",
                "PDF File Name",
                "Image File Name",
                "OCR Text",
                "Payee Match",
            ]
        )

        for input_record, pdf_record, image_record, ocr_record in records:
            writer.writerow(
                [
                    input_record.id,
                    input_record.batch_uuid,
                    input_record.account_number,
                    input_record.check_number,
                    input_record.amount,
                    input_record.payee_1,
                    input_record.payee_2,
                    input_record.issue_date,
                    pdf_record.pdf_name,
                    f"{input_record.guid}_{image_record.id}.png",  # Assuming image filenames are structured like this
                    ocr_record.extracted_text,
                    ocr_record.payee_match,
                ]
            )

    print(f"Export completed. File saved as {filename}")
    return filename
