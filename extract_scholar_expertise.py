import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Load cleaned titles
df = pd.read_csv("data/processed/scholar_titles_cleaned.csv")

print("Loaded Shape:", df.shape)

# Build TF-IDF matrix
vectorizer = TfidfVectorizer(
    max_features=1000,
    ngram_range=(1, 2),   # single words + 2-word phrases
    min_df=1
)

X = vectorizer.fit_transform(df["Cleaned_Title"])

terms = vectorizer.get_feature_names_out()

# Extract top keywords from each title
def get_top_keywords(row_vector, top_n=5):
    row = row_vector.toarray().flatten()

    # highest tf-idf scores first
    top_indices = row.argsort()[-top_n:][::-1]

    keywords = []
    for idx in top_indices:
        if row[idx] > 0:
            keywords.append(terms[idx])

    return ", ".join(keywords)

df["ScholarKeywords"] = [
    get_top_keywords(X[i])
    for i in range(X.shape[0])
]

print(df[["FacultyID", "ScholarKeywords"]].head())

# Save title-level keywords
df.to_csv(
    "data/processed/scholar_keywords.csv",
    index=False
)

print("scholar_keywords.csv created ✅")