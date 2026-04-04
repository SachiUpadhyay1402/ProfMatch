import pandas as pd
from rapidfuzz import process, fuzz

# Load mapping (website ground truth)
mapping = pd.read_csv("data/processed/faculty_name_mapping.csv")

# Load scholar selenium
sel = pd.read_csv(
    "data/raw/faculty_publications_selenium.csv",
    header=None,
    names=["Name","ScholarID","ProfileLink","Title"]
)

# Load scholar manual
man = pd.read_csv(
    "data/raw/scholar_manual.csv",
    header=None,
    names=["Name","ScholarID","ProfileLink","Title"]
)

# Unique scholar names
scholar_names = pd.concat([sel["Name"], man["Name"]]).dropna().unique()

website_names = mapping["Name"].tolist()

rows = []

for sname in scholar_names:
    match = process.extractOne(
        sname,
        website_names,
        scorer=fuzz.token_sort_ratio
    )
    
    rows.append({
        "ScholarName": sname,
        "SuggestedWebsiteName": match[0],
        "SimilarityScore": match[1]
    })

out = pd.DataFrame(rows).sort_values(by="SimilarityScore", ascending=False)

out.to_csv("data/processed/name_match_suggestions.csv", index=False)

print("Name Matching Suggestions Created")