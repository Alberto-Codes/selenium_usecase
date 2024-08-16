from sqlalchemy import update, select, func
from sqlalchemy.orm import Session
from prefect import task, flow
from src.db.db_setup import TblRCNBatchStatus, TblRCNInput, get_session, generate_uuid
import datetime

@task
def create_batch(session: Session):
    """
    Create a new batch and set its status to 'pending'.
    """
    batch_id = generate_uuid()
    new_batch = TblRCNBatchStatus(id=batch_id, status="pending", failed_records=0)
    session.add(new_batch)
    session.commit()
    return batch_id

@task
def update_batch_status(session: Session, batch_id: str, status: str):
    """
    Update the status of the batch to the specified status.
    """
    session.execute(
        update(TblRCNBatchStatus)
        .where(TblRCNBatchStatus.id == batch_id)
        .values(status=status)
    )
    session.commit()

@task
def select_and_update_records(session: Session, batch_id: str, limit: int):
    """
    Select a specified number of records, update their status, and associate them with the batch ID.
    """
    stmt = (
        select(TblRCNInput)
        .where(TblRCNInput.status == 'pending')
        .limit(limit)
    )
    records = session.execute(stmt).scalars().all()

    for record in records:
        record.status = 'in_progress'
        record.batch_uuid = batch_id

    session.commit()
    return records

@task
def print_records(records):
    """
    Print the selected records to stdout.
    """
    for record in records:
        print(f"Record ID: {record.id}, Account: {record.account_number}, Status: {record.status}, Batch ID: {record.batch_uuid}")

@flow
def batch_processing_workflow(limit: int = 10):
    """
    Main workflow to handle batch processing.
    """
    session = get_session()
    
    # Step 1: Create a new batch
    batch_id = create_batch(session)

    # Step 2: Update batch status to 'in_progress'
    update_batch_status(session, batch_id, 'in_progress')

    # Step 3: Select and update input records with batch ID
    records = select_and_update_records(session, batch_id, limit)

    # Step 4: Print out the selected records
    print_records(records)
    
    # Optionally: Update batch status to 'completed'
    # update_batch_status(session, batch_id, 'completed')

    session.close()
