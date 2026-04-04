import pandas as pd

df = pd.read_csv("data/processed/faculty_structured.csv")

# Remove bios that are just links
df["Bio"] = df["Bio"].apply(
    lambda x: "" if isinstance(x, str) and "http" in x.lower() else x
)

df.to_csv("data/processed/faculty_structured_cleaned.csv", index=False)

print("Clean file saved.")