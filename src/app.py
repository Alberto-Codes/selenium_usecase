from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Initialize WebDriver
driver = webdriver.Chrome()  # Adjust if using a different browser

# Load the website
driver.get("https://example-java-website.com")  # Replace with the actual URL

# Wait for the page to fully load and the target button to be clickable
wait = WebDriverWait(driver, 20)
button = wait.until(EC.element_to_be_clickable((By.ID, "button_id")))  # Replace with actual button id

# Click the button
button.click()

# Load your dataset
df = pd.read_csv("data.csv")  # Adjust according to your dataset source

# Iterate through the dataset and input values
for index, row in df.iterrows():
    acct_number = row['acctnumber']
    check_number = row['checknumber']
    amount = row['amount']

    # Wait for and input values into respective fields
    acct_input = wait.until(EC.visibility_of_element_located((By.ID, "acct_input_id")))
    check_input = driver.find_element(By.ID, "check_input_id")
    amount_input = driver.find_element(By.ID, "amount_input_id")

    acct_input.clear()
    acct_input.send_keys(acct_number)

    check_input.clear()
    check_input.send_keys(check_number)

    amount_input.clear()
    amount_input.send_keys(amount)

    # Press the search button
    search_button = driver.find_element(By.ID, "search_button_id")
    search_button.click()

    # Wait for the new page to load and the checkbox to be clickable
    checkbox = wait.until(EC.element_to_be_clickable((By.ID, "checkbox_id")))
    checkbox.click()

    # Press the download button
    download_button = driver.find_element(By.ID, "download_button_id")
    download_button.click()

# Close the browser after all operations are done
driver.quit()
