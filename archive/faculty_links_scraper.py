from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://mitwpu.edu.in/faculty-members")

# Give page time to fully render
driver.implicitly_wait(5)

# Get all anchor tags
links = driver.find_elements(By.TAG_NAME, "a")

profile_urls = []

for link in links:
    href = link.get_attribute("href")
    if href and href.startswith("https://mitwpu.edu.in/faculty/"):
        profile_urls.append(href)

# Remove duplicates
profile_urls = list(set(profile_urls))

print("Total unique faculty profile links:", len(profile_urls))

driver.quit()