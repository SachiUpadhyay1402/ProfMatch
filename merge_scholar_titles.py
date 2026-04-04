import pandas as pd

# -----------------------------
# Load faculty name mapping
# -----------------------------
mapping = pd.read_csv("data/processed/faculty_name_mapping.csv")

# Keep only rows where ScholarName is filled
mapping = mapping.dropna(subset=["ScholarName"])

# Only keep the columns needed for merging
mapping = mapping[["FacultyID", "ScholarName"]]


# -----------------------------
# Load selenium scholar data
# -----------------------------
selenium_df = pd.read_csv(
    "data/raw/faculty_publications_selenium.csv",
    header=None,
    names=["ScholarName", "ScholarID", "ProfileLink", "Title"]
)

# -----------------------------
# Load manual scholar data
# -----------------------------
manual_df = pd.read_csv(
    "data/raw/scholar_manual.csv",
    header=None,
    names=["ScholarName", "ScholarID", "ProfileLink", "Title"]
)

# -----------------------------
# Combine both scholar datasets
# -----------------------------
scholar_df = pd.concat([selenium_df, manual_df], ignore_index=True)

print("Combined Scholar Rows:", scholar_df.shape[0])

# -----------------------------
# Merge with FacultyID mapping
# -----------------------------
merged_df = scholar_df.merge(
    mapping,
    on="ScholarName",
    how="left"
)

# -----------------------------
# Keep only matched rows
# -----------------------------
matched_df = merged_df.dropna(subset=["FacultyID"])

print("Matched Rows:", matched_df.shape[0])

# -----------------------------
# Remove duplicate titles per faculty
# -----------------------------
matched_df = matched_df.drop_duplicates(subset=["FacultyID", "Title"])

print("After Dedup:", matched_df.shape[0])

# -----------------------------
# Final output columns
# -----------------------------
matched_df = matched_df[
    ["FacultyID", "ScholarName", "Title", "ScholarID", "ProfileLink"]
]

# -----------------------------
# Save master scholar titles file
# -----------------------------
matched_df.to_csv(
    "data/processed/scholar_titles_master.csv",
    index=False
)

print("scholar_titles_master.csv created ✅")
print(matched_df.head())