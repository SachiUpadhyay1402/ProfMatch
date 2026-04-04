from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Initialize driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open a website
driver.get("https://www.google.com")

print("Browser launched successfully!")

driver.quit()