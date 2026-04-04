import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load structured data
df = pd.read_csv("data/processed/faculty_structured_cleaned.csv")

# Combine searchable fields
df["Searchable_Text"] = (
    (df["Research_Areas"].fillna("") + " ") * 3 +
    (df["Publications"].fillna("") + " ") * 2 +
    (df["Bio"].fillna("") + " ")
)

# Initialize vectorizer
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(df["Searchable_Text"])

def search_faculty(query, top_n=5):
    query_vec = vectorizer.transform([query])
    similarity_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    df["Similarity"] = similarity_scores
    results = df.sort_values(by="Similarity", ascending=False).head(top_n)

    return results

if __name__ == "__main__":
    query = input("Tell me your research interest: ")

    results = search_faculty(query, top_n=5)
    
    results = results[results["Similarity"] > 0]
    
    if results.empty:
        print("\nSorry, no relevant faculty found for your query.")
        exit()

    print("\nBased on your interest, here are the top matching faculty members:\n")

    for idx, row in enumerate(results.itertuples(), start=1):
        
        # Safe designation handling
        designation = row.Designation if pd.notna(row.Designation) else "Faculty Member"
        
        # Safe bio handling
        bio_text = row.Bio
        
        if not isinstance(bio_text, str) or bio_text.strip() == "":
            preview = "No bio information available."
        else:
            sentences = re.split(r'(?<=[.!?]) +', bio_text)
            preview = " ".join(sentences[:2]).strip()
            
        match_percentage = round(row.Similarity * 100)
        
        print(f"{idx}. {row.Name} – {designation}")
        print(f"Match Strength: {match_percentage}%")
        print(f"Bio Preview: {preview}")
        print(f"Profile: {row.Profile_URL}\n")