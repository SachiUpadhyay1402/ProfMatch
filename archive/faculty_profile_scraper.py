import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://mitwpu.edu.in/faculty-members"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(BASE_URL)
driver.implicitly_wait(5)

# Collect profile links
links = driver.find_elements(By.TAG_NAME, "a")

profile_urls = []

for link in links:
    href = link.get_attribute("href")
    if href and href.startswith("https://mitwpu.edu.in/faculty/"):
        profile_urls.append(href)

profile_urls = list(set(profile_urls))

print(f"Total profiles found: {len(profile_urls)}")

# Prepare CSV
with open("data/raw/faculty_profiles_raw.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Profile_URL", "Full_Text"])

    for index, url in enumerate(profile_urls):
        print(f"Scraping {index+1}/{len(profile_urls)}")

        driver.get(url)
        time.sleep(2)

        try:
            name = driver.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            name = "N/A"

        try:
            content_section = driver.find_element(By.CSS_SELECTOR, "section.faculty-details-sec")
            full_text = content_section.text
        except:
            full_text = " "

        writer.writerow([name, url, full_text])

driver.quit()

print("Scraping completed. Data saved to data/raw/faculty_profiles_raw.csv")