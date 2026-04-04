import pandas as pd

df = pd.read_csv("data/processed/faculty_structured.csv")

# remove duplicates if any
df = df.drop_duplicates(subset=["Name"]).reset_index(drop=True)

# create FacultyID
df["FacultyID"] = ["F" + str(i+1).zfill(3) for i in range(len(df))]

mapping = df[["FacultyID","Name"]]

mapping.to_csv("data/processed/faculty_name_mapping.csv", index=False)

print("Faculty Mapping Created")
print(mapping.head())