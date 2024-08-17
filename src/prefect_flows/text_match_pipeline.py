from prefect import flow, task
from sqlalchemy.orm import Session
from src.db.db_setup import get_session, TblRCNOCRResult, TblRCNInput
from src.utils.payee_matcher import PayeeMatcher


@task
def fetch_ocr_records_for_matching(session: Session):
    # Fetch OCR records that need payee matching (assuming raw preprocessing and status 'text_extracted')
    ocr_records = session.query(TblRCNOCRResult).filter_by(preprocessing_type="raw").all()
    return ocr_records


@task
def match_and_update_payees(session: Session, ocr_record, matcher: PayeeMatcher):
    # Fetch the related input record to get payee_1 and payee_2
    input_record = session.query(TblRCNInput).filter_by(id=ocr_record.image.input_table_id).first()
    payees = [input_record.payee_1, input_record.payee_2]

    # Perform the payee matching
    matched, possible_matches = matcher.match_payees(ocr_record.extracted_text, payees)

    # Update OCR record with the payee matching results
    ocr_record.payee_match = "yes" if any(matched.values()) else "no"
    session.commit()

    # Update the input record's status to 'payee_match_attempted'
    input_record.status = "payee_match_attempted"
    session.commit()

    return matched, possible_matches


@flow
def payee_matching_flow():
    session = get_session()

    # Instantiate the PayeeMatcher
    matcher = PayeeMatcher()

    ocr_records = fetch_ocr_records_for_matching(session).result()

    for ocr_record in ocr_records:
        match_and_update_payees(session, ocr_record, matcher)

    session.close()
