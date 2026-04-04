import pandas as pd
import re
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")

df = pd.read_csv("data/processed/scholar_titles_master.csv")

print("Original Shape:", df.shape)

# remove rows with missing titles
df = df.dropna(subset=["Title"])

# lowercase
df["Title"] = df["Title"].str.lower()

# remove punctuation + digits
df["Title"] = df["Title"].apply(
    lambda x: re.sub(r"[^a-z\s]", " ", x)
)

# normalize spaces
df["Title"] = df["Title"].apply(
    lambda x: re.sub(r"\s+", " ", x).strip()
)

# standard stopwords
stop_words = set(stopwords.words("english"))

# additional academic filler words to remove
custom_words = {
    "using", "based", "approach", "analysis", "study", "method",
    "system", "model", "paper", "review", "framework", "new"
}

stop_words = stop_words.union(custom_words)

def clean_text(text):
    words = [
        word for word in text.split()
        if word not in stop_words and len(word) > 2
    ]
    return " ".join(words)

df["Cleaned_Title"] = df["Title"].apply(clean_text)

# remove duplicates after cleaning
df = df.drop_duplicates(subset=["FacultyID", "Cleaned_Title"])

print("Cleaned Shape:", df.shape)

df.to_csv(
    "data/processed/scholar_titles_cleaned.csv",
    index=False
)

print("scholar_titles_cleaned.csv created ✅")
print(df[["FacultyID", "Title", "Cleaned_Title"]].head())