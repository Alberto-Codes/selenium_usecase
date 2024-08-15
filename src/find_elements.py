from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize WebDriver
driver = webdriver.Chrome()  # Adjust if using a different browser
driver.get("https://example-java-website.com")  # Replace with the actual URL

# Find all elements in the DOM
elements = driver.find_elements(By.XPATH, "//*")

# Print out all visible elements
for element in elements:
    if element.is_displayed():
        print(
            f"Tag: {element.tag_name}, Text: {element.text}, ID: {element.get_attribute('id')}, Class: {element.get_attribute('class')}"
        )

# Close the browser after you are done
driver.quit()
