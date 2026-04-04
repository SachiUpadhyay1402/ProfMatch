import pandas as pd
from collections import Counter

# Load dataset
df = pd.read_csv("data/raw/faculty_profiles_raw.csv")

print("Total Profiles:", len(df))

heading_counter = Counter()

for text in df["Full_Text"]:
    lines = text.split("\n")
    for line in lines:
        clean_line = line.strip()
        if (
            len(clean_line) < 40 and
            clean_line.replace(" ", "").isalpha()
        ):
            heading_counter[clean_line] += 1

# Keep only headings that appear more than 20 times
common_headings = {k: v for k, v in heading_counter.items() if v > 20}

with open("data/processed/common_headings.txt", "w", encoding="utf-8") as f:
    for heading, count in sorted(common_headings.items()):
        f.write(f"{heading} -> {count}\n")

print("Common headings saved to data/processed/common_headings.txt")