import pandas as pd

df = pd.read_csv("data/processed/scholar_keywords.csv")

# Combine all keywords belonging to same faculty
faculty_expertise = (
    df.groupby("FacultyID")["ScholarKeywords"]
    .apply(lambda x: ", ".join(x))
    .reset_index()
)

faculty_expertise.rename(
    columns={"ScholarKeywords": "ScholarExpertise"},
    inplace=True
)

print("Faculty Count:", faculty_expertise.shape[0])
print(faculty_expertise.head())

faculty_expertise.to_csv(
    "data/processed/scholar_expertise_final.csv",
    index=False
)

print("scholar_expertise_final.csv created ✅")