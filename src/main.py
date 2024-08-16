import os

from data_loader import load_dataset_into_db
from ocr_workflow import process_and_store_image
from utils.create_fictitious_data import generate_fictitious_data

# Define paths
image_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "data/stored_jpegs")
)
output_excel_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/fictitious_data.xlsx")
)
db_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/check_recon.db")
)


def main():
    # Generate fictitious data
    # generate_fictitious_data(image_dir, output_excel_path)
    # print(f"Fictitious data generated and saved to {output_excel_path}")

    # Load dataset into the database
    load_dataset_into_db(output_excel_path, db_path)
    print(f"Data loaded into the database at {db_path}")


if __name__ == "__main__":
    main()
