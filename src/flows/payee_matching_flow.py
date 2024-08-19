from prefect import flow, task

from src.db.db_connect import get_session
from src.services.payee_matching_service import PayeeMatchingService


@task
def process_ocr_records(service: PayeeMatchingService) -> None:
    """
    Processes OCR records by fetching them and performing payee matching.

    Args:
        service (PayeeMatchingService): The service handling the payee matching process.

    Returns:
        None
    """
    ocr_records = service.fetch_ocr_records()

    for ocr_record in ocr_records:
        service.match_and_update_payees(ocr_record)


@flow
def payee_matching_flow() -> None:
    """
    Orchestrates the payee matching process by initializing the session and service,
    then processing the OCR records.

    Returns:
        None
    """
    session = get_session()
    service = PayeeMatchingService(session)

    process_ocr_records(service)

    session.close()
