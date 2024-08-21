from typing import List

from prefect import flow, task

from src.db.db_connect import duckdb_session as session
from src.services.batch_service import BatchService


@task
def create_and_process_batch_task(service: BatchService, limit: int) -> tuple:
    """
    Creates and processes a batch of records using the given BatchService.

    Args:
        service (BatchService): The batch service to use for processing.
        limit (int): The maximum number of pending records to process.

    Returns:
        tuple: A tuple containing the batch ID and the list of processed records.
    """
    return service.create_and_process_batch(limit)


@task
def complete_batch_task(service: BatchService, batch_id: str) -> None:
    """
    Marks a batch as completed using the given BatchService.

    Args:
        service (BatchService): The batch service to use for completing the batch.
        batch_id (str): The ID of the batch to complete.

    Returns:
        None
    """
    service.complete_batch(batch_id)


@task
def print_records(records: List) -> None:
    """
    Prints details of the processed records.

    Args:
        records (List): The list of records to print.

    Returns:
        None
    """
    for record in records:
        print(
            f"Record ID: {record.id}, Account: {record.account_number}, Status: {record.status}, Batch ID: {record.batch_uuid}"
        )


@flow
def batch_processing_workflow(limit: int = 10) -> None:
    """
    Prefect flow for batch processing of records.

    Args:
        limit (int): The maximum number of pending records to process. Defaults to 10.

    Returns:
        None
    """
    batch_service = BatchService(session)

    batch_id, records = create_and_process_batch_task(batch_service, limit)

    print_records(records)

    complete_batch_task(batch_service, batch_id)

    session.close()
