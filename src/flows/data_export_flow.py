from prefect import flow, task

from src.db.db_connect import engine, get_session
from src.services.data_export_service import DataExportService


@task
def export_data_task(target_directory: str) -> None:
    """
    Task to export data and associated files to the specified target directory.

    This task initializes a database session, creates a `DataExportService`
    instance, and invokes its `export_data_with_files` method to handle
    the export process.

    Args:
        target_directory (str): The path to the directory where data and
            files should be exported.
    """
    session = get_session(engine)
    try:
        export_service = DataExportService(session, target_directory)
        export_service.export_data_with_files()
    finally:
        session.close()


@flow
def export_data_flow(target_directory: str = "path/to/output_directory") -> None:
    """
    Prefect flow to manage the data export process.

    This flow runs the `export_data_task`, which handles exporting data and
    associated files to the specified target directory.

    Args:
        target_directory (str, optional): The path to the directory where data
            and files should be exported. Defaults to
            "path/to/output_directory".
    """
    export_data_task(target_directory)


if __name__ == "__main__":
    export_data_flow()
