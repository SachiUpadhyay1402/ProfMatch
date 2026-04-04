import pandas as pd
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

# --------------------------------------------------
# Download NLTK resources (first run only)
# --------------------------------------------------
nltk.download("wordnet")
nltk.download("omw-1.4")
nltk.download("stopwords")

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))
custom_stopwords = {
    "book", "chapter", "publication", "isbn", "paper", "author",
    "presented", "conference", "journal", "study", "research",
    "university", "college", "professor", "assistant", "associate",
    "working", "currently", "publication", "published"
}

stop_words.update(custom_stopwords)

# --------------------------------------------------
# Load files
# --------------------------------------------------
df = pd.read_csv("data/processed/faculty_expertise_corpus.csv")
structured_df = pd.read_csv("data/processed/faculty_structured.csv")

# Clean column names in case there are hidden spaces
df.columns = df.columns.str.strip()
structured_df.columns = structured_df.columns.str.strip()

# --------------------------------------------------
# Keep only needed columns from faculty_structured.csv
# --------------------------------------------------
structured_df = structured_df[["Name", "Publications", "Bio"]]

# Fill missing values before merge
structured_df["Publications"] = structured_df["Publications"].fillna("")
structured_df["Bio"] = structured_df["Bio"].fillna("")

# --------------------------------------------------
# Merge Publications + Bio into final expertise corpus
# --------------------------------------------------
df = df.merge(
    structured_df,
    on="Name",
    how="left"
)

# --------------------------------------------------
# Fill missing values
# --------------------------------------------------
for col in ["ScholarExpertise", "WebsiteExpertise", "Publications", "Bio"]:
    if col not in df.columns:
        df[col] = ""

    df[col] = df[col].fillna("")

# --------------------------------------------------
# Build weighted searchable text
# Strongest weight -> Google Scholar expertise
# Then MIT research areas
# Then publication list
# Then bio
# --------------------------------------------------
df["Searchable_Text"] = (
    (df["ScholarExpertise"] + " ") * 8 +
    (df["WebsiteExpertise"] + " ") * 4 +
    (df["Publications"] + " ") * 2 +
    (df["Bio"] + " ")
)

# --------------------------------------------------
# Text cleaning + lemmatization
# --------------------------------------------------
def clean_text(text):
    text = str(text).lower()

    # Remove punctuation / numbers
    text = re.sub(r"[^a-zA-Z\s]", " ", text)

    cleaned_words = []

    for word in text.split():

        # Remove stopwords
        if word in stop_words:
            continue

        # Lemmatize word
        word = lemmatizer.lemmatize(word)

        # Skip very short words
        if len(word) > 2:
            cleaned_words.append(word)

    return " ".join(cleaned_words)

# Apply cleaning
df["Searchable_Text"] = df["Searchable_Text"].apply(clean_text)

# --------------------------------------------------
# Save output
# --------------------------------------------------
output_file = "data/processed/faculty_search_ready.csv"
df.to_csv(output_file, index=False)

# --------------------------------------------------
# Preview
# --------------------------------------------------
sample_df = df[
    (df["ScholarExpertise"] != "") |
    (df["WebsiteExpertise"] != "")
].head(3)

print("\nSample with expertise present:\n")

for _, row in sample_df.iterrows():
    print("=" * 80)
    print("Name:", row["Name"])
    print("\nWebsiteExpertise:")
    print(row["WebsiteExpertise"])
    print("\nScholarExpertise:")
    print(row["ScholarExpertise"])
    print("\nSearchable_Text:")
    print(row["Searchable_Text"][:1000])   # first 1000 chars only
    print()