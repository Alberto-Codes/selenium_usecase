from prefect import flow, task

from src.db.db_setup import get_session
from src.utils.payee_mismatch_exporter import (export_to_csv,
                                               fetch_records_for_export)


@task
def fetch_records(session, batch_id):
    return fetch_records_for_export(session)


@task
def save_to_csv(records, batch_id):
    return export_to_csv(records, batch_id)


@flow
def payee_mismatch_export_flow(batch_id):
    session = get_session()

    records = fetch_records(session, batch_id).result()

    if records:
        save_to_csv(records, batch_id)
    else:
        print("No records found with payee match sum of 0.")

    session.close()
