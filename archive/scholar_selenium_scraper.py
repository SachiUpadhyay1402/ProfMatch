import time
import random
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------- CLEAN SCHOLAR LINKS ----------------
def clean_scholar(x):
    if pd.isna(x):
        return None

    x = str(x).strip()

    if "scholar.google" in x:
        m = re.search(r'user=([a-zA-Z0-9_-]+)', x)
        if m:
            sid = m.group(1)
            return f"https://scholar.google.com/citations?user={sid}"

    if re.fullmatch(r'[a-zA-Z0-9_-]{6,}', x):
        return f"https://scholar.google.com/citations?user={x}"

    return None


def extract_id(url):
    m = re.search(r'user=([a-zA-Z0-9_-]+)', url)
    return m.group(1) if m else None


# ---------------- SETUP BROWSER ----------------
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

# ⭐ Stability flags
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.add_argument("--remote-debugging-port=9222")

driver_path = ChromeDriverManager().install()

driver = webdriver.Chrome(
    service=Service(driver_path),
    options=options
)

BATCH_SIZE = 8
faculty_counter = 0


# ---------------- LOAD DATA ----------------
df = pd.read_csv("data/processed/faculty_structured.csv")
df.columns = df.columns.str.strip()

df["Scholar_Link"] = df["Google_Scholar"].apply(clean_scholar)
df = df[df["Scholar_Link"].notna()].reset_index(drop=True)

print("Valid Scholar Profiles:", len(df))


# ---------------- RESUME SUPPORT ----------------
output_path = "data/processed/faculty_publications_selenium.csv"

processed = set()

try:
    old = pd.read_csv(output_path)

    counts = old.groupby("Scholar_Link")["Title"].count()

    # Only mark faculty done if >=10 titles already saved
    processed = set(counts[counts >= 10].index)

    print("Fully processed faculty:", len(processed))

except:
    print("Fresh run")

# ---------------- SCRAPE FUNCTION ----------------
def scrape_titles(profile_url):

    # ⭐ OPEN PROFILE PAGE (CRITICAL)
    try:
        driver.get(profile_url)
    except:
        print("Navigation failed")
        return []

    time.sleep(random.randint(4,7))

    # ⭐ Handle Chrome crash / data:,
    if driver.current_url.startswith("data"):
        print("Browser failed to load page")
        return []

    # ⭐ CAPTCHA detection
    if "sorry" in driver.current_url.lower():
        input("CAPTCHA detected. Solve it manually then press ENTER...")

    # ⭐ Wait for publication table properly
    try:
        WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.CLASS_NAME,"gsc_a_at"))
        )
    except:
        print("Publications not loaded")
        return []

    # ⭐ Human scroll behaviour
    driver.execute_script(f"window.scrollBy(0,{random.randint(200,600)})")
    time.sleep(random.uniform(1.5,3.5))

    titles = []
    seen = set()

    prev_count = -1
    
    while True:
        pubs = driver.find_elements(By.CLASS_NAME, "gsc_a_at")

        for p in pubs:
            t = p.text.strip()
            if t and t not in seen:
                titles.append(t)
                seen.add(t)

        # EXIT 1 → enough titles
        if len(titles) >= 10:
            break

        # EXIT 2 → no new titles added (profile finished)
        if len(titles) == prev_count:
            print("Profile exhausted")
            break

        prev_count = len(titles)
        
        try:
            show_more = driver.find_element(By.ID, "gsc_bpf_more")

            if "disabled" in show_more.get_attribute("class"):
                print("No more publications button")
                break

            driver.execute_script(f"window.scrollBy(0,{random.randint(300,800)})")
            time.sleep(random.uniform(1.5,3.5))

            show_more.click()
            time.sleep(random.randint(3,6))

        except:
            print("Show more not found")
            break

    return titles[:10]


# ---------------- MAIN LOOP ----------------
for idx, row in df.iterrows():

    # ⭐ Restart browser batching
    if faculty_counter % BATCH_SIZE == 0 and faculty_counter != 0:
        print("Restarting browser session...")
        driver.quit()
        time.sleep(random.randint(25,50))

        driver = webdriver.Chrome(
            service=Service(driver_path),
            options=options
        )

    link = row["Scholar_Link"]

    if link in processed:
        print("Already done:", row["Name"])
        continue

    print(f"\nScraping: {row['Name']}")

    try:
        titles = scrape_titles(link)

        rows = []
        for t in titles:
            rows.append({
                "Name": row["Name"],
                "Scholar_ID": extract_id(link),
                "Scholar_Link": link,
                "Title": t
            })

        if rows:
            pd.DataFrame(rows).to_csv(
                output_path,
                mode="a",
                header=not pd.io.common.file_exists(output_path),
                index=False
            )

    except Exception as e:
        print("Failed:", e)
        continue

    faculty_counter += 1

    # ⭐ Longer human delay
    time.sleep(random.randint(45,75))

    # ⭐ Cooldown
    if faculty_counter % 5 == 0:
        print("Cooling down...")
        time.sleep(random.randint(120,240))


print("DONE SCRAPING")
driver.quit()