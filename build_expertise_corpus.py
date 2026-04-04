import pandas as pd

# Load MIT faculty data
website_df = pd.read_csv("data/processed/faculty_structured.csv")

# Load FacultyID mapping
mapping_df = pd.read_csv("data/processed/faculty_name_mapping.csv")

# Add FacultyID into website dataset
website_df = website_df.merge(
    mapping_df[["FacultyID", "Name"]],
    on="Name",
    how="left"
)

# Use MIT research areas as website expertise
website_df["WebsiteExpertise"] = website_df["Research_Areas"].fillna("")

# Keep only required columns
website_df = website_df[
    ["FacultyID", "Name", "Designation", "WebsiteExpertise"]
]

# Load scholar expertise
scholar_df = pd.read_csv("data/processed/scholar_expertise_final.csv")

# Merge scholar expertise with MIT data
final_df = website_df.merge(
    scholar_df,
    on="FacultyID",
    how="left"
)

# Replace missing scholar expertise with blank
final_df["ScholarExpertise"] = final_df["ScholarExpertise"].fillna("")

# Give more weight to publication-based expertise
final_df["FinalExpertise"] = (
    final_df["WebsiteExpertise"].astype(str) + " " +
    final_df["ScholarExpertise"].astype(str) + " " +
    final_df["ScholarExpertise"].astype(str)
)

# Clean extra spaces
final_df["FinalExpertise"] = (
    final_df["FinalExpertise"]
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# Save final expertise corpus
final_df.to_csv(
    "data/processed/faculty_expertise_corpus.csv",
    index=False
)

print("faculty_expertise_corpus.csv created ✅")
print("Rows:", final_df.shape[0])
print(final_df[
    ["FacultyID", "Name", "WebsiteExpertise", "ScholarExpertise"]
].head())