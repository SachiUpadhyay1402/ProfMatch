import pandas as pd
import re

df = pd.read_csv("data/raw/faculty_profiles_raw.csv")

structured_data = []

for _, row in df.iterrows():
    name = row["Name"]
    url = row["Profile_URL"]
    text = row["Full_Text"]

    lines = text.split("\n")

    designation = ""
    bio = ""
    research = ""
    publications = ""
    scholar = ""
    orcid = ""
    scopus = ""

    current_section = None

    for line in lines:
        clean = line.strip()

        if clean in ["Assistant Professor", "Associate Professor", "Professor"]:
            designation = clean

        elif clean.lower() in ["bio"]:
            current_section = "bio"

        elif clean.lower() in ["research area", "research areas", "research interests"]:
            current_section = "research"

        elif clean.lower() in ["publication", "publications", "publications list", "research papers"]:
            current_section = "publications"

        elif "google scholar" in clean.lower():
            scholar = clean

        elif "orcid" in clean.lower():
            orcid = clean

        elif "scopus" in clean.lower():
            scopus = clean

        else:
            if current_section == "bio":
                bio += clean + " "
            elif current_section == "research":
                research += clean + " "
            elif current_section == "publications":
                publications += clean + " "

    structured_data.append({
        "Name": name,
        "Profile_URL": url,
        "Designation": designation,
        "Bio": bio.strip(),
        "Research_Areas": research.strip(),
        "Publications": publications.strip(),
        "Google_Scholar": scholar,
        "ORCID": orcid,
        "Scopus": scopus
    })

structured_df = pd.DataFrame(structured_data)
structured_df.to_csv("data/processed/faculty_structured.csv", index=False)

print("Structured dataset saved to data/processed/faculty_structured.csv")