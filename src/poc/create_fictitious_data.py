import os
import uuid

import pandas as pd
from PIL import Image

# Directory containing the images
image_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/stored_jpegs")
)

# Output Excel file path
output_excel_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/fictitious_data.xlsx")
)


def generate_fictitious_data(image_dir, output_excel_path):
    # List to store data
    data = []

    # Iterate over all images in the directory
    for image_name in os.listdir(image_dir):
        if image_name.lower().endswith((".png", ".jpg", ".jpeg")):
            # Generate a UUID for the image
            image_uuid = str(uuid.uuid4())

            # Rename the image with the UUID
            old_image_path = os.path.join(image_dir, image_name)
            new_image_name = f"{image_uuid}.jpg"
            new_image_path = os.path.join(image_dir, new_image_name)
            os.rename(old_image_path, new_image_path)

            # Create fictitious data
            fictitious_record = {
                "uuid": image_uuid,
                "AcctNumber": str(uuid.uuid4().int)[:6],  # Random 6-digit number
                "CheckNumber": str(uuid.uuid4().int)[:4],  # Random 4-digit number
                "Amount": f"{round(uuid.uuid4().int % 1000 + 100, 2)}",  # Random amount between 100 and 1100
                "Date": "2023-01-01",  # Fixed date for simplicity
                "Payee": "John Doe",  # Fixed payee for simplicity
            }
            data.append(fictitious_record)

    # Create a DataFrame from the data
    df = pd.DataFrame(data)

    # Save the DataFrame to an Excel file
    df.to_excel(output_excel_path, index=False)
    print(f"Fictitious data saved to {output_excel_path}")


if __name__ == "__main__":
    generate_fictitious_data(image_dir, output_excel_path)
