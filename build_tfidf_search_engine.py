import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

# --------------------------------------------------
# Load search-ready corpus
# --------------------------------------------------
df = pd.read_csv("data/processed/faculty_search_ready.csv")

# Fill any missing text just in case
df["Searchable_Text"] = df["Searchable_Text"].fillna("")

# --------------------------------------------------
# Build TF-IDF vectors
# --------------------------------------------------
vectorizer = TfidfVectorizer(
    stop_words="english",
    lowercase=True,
    ngram_range=(1, 3),
    min_df=2,
    max_df=0.85,
    sublinear_tf=True,
    max_features=10000
)

faculty_vectors = vectorizer.fit_transform(df["Searchable_Text"])

print("TF-IDF matrix shape:", faculty_vectors.shape)

# --------------------------------------------------
# Save vectorizer + matrix for later Streamlit/chatbot
# --------------------------------------------------
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")
joblib.dump(faculty_vectors, "faculty_vectors.pkl")

print("Saved tfidf_vectorizer.pkl and faculty_vectors.pkl")

# --------------------------------------------------
# Search function
# --------------------------------------------------
def search_faculty(query, top_k=5):

    # Vectorize query
    query_vector = vectorizer.transform([query])

    # Cosine similarity
    similarity_scores = cosine_similarity(
        query_vector,
        faculty_vectors
    ).flatten()

    # Query keywords that actually exist in the TF-IDF vocabulary
    query_terms = [
        term.lower()
        for term in query.split()
        if term.lower() in vectorizer.vocabulary_
    ]

    top_indices = similarity_scores.argsort()[::-1][:top_k]

    results = []

    for idx in top_indices:
        score = similarity_scores[idx]

        if score <= 0:
            continue

        row = df.iloc[idx]

        matched_terms = []

        # Find which query terms appear in this faculty's searchable text
        searchable_text = str(row["Searchable_Text"])

        for term in query_terms:
            if term in searchable_text:
                matched_terms.append(term)

        # Remove duplicates while keeping order
        matched_terms = list(dict.fromkeys(matched_terms))

        results.append({
            "Name": row["Name"],
            "Designation": row["Designation"],
            "Score": round(float(score), 4),
            "WebsiteExpertise": row["WebsiteExpertise"],
            "ScholarExpertise": row["ScholarExpertise"],
            "MatchedTerms": matched_terms,
            "MatchedText": searchable_text[:400]
        })

    return results

# --------------------------------------------------
# Interactive search loop
# --------------------------------------------------
print("\nFaculty Search Engine Ready!")
print("Type a query like:")
print("- machine learning healthcare")
print("- blockchain security")
print("- natural language processing")
print("- marketing digital payment")
print("\nType 'exit' to quit.\n")

while True:
    query = input("Search Query: ").strip()

    if query.lower() == "exit":
        print("Exiting search engine...")
        break

    if not query:
        print("Please enter a query.\n")
        continue

    results = search_faculty(query)

    if not results:
        print("\nNo relevant faculty found.\n")
        continue

    print("\nTop Matching Faculty:\n")

    for i, faculty in enumerate(results, start=1):
        print("=" * 80)
        print(f"{i}. {faculty['Name']}")
        print(f"Designation  : {faculty['Designation']}")
        print(f"Score        : {faculty['Score']}")
        
        if faculty['MatchedTerms']:
            print(
                "Matched Terms: " + ", ".join(faculty['MatchedTerms'])
            )

        if pd.notna(faculty['WebsiteExpertise']) and str(faculty['WebsiteExpertise']) != 'nan':
            print(f"Website Exp. : {faculty['WebsiteExpertise']}")

        if pd.notna(faculty['ScholarExpertise']) and str(faculty['ScholarExpertise']) != 'nan':
            print(f"Scholar Exp. : {faculty['ScholarExpertise']}")

        print(f"Matched Text : {faculty['MatchedText']}")