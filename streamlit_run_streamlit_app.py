import streamlit as st
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="MIT Faculty Expertise Search",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 MIT Faculty Expertise Search Engine")
st.markdown(
    "Search for faculty based on research interests, publications, and expertise."
)

# --------------------------------------------------
# Load data + saved TF-IDF objects
# --------------------------------------------------
@st.cache_data

def load_data():
    df = pd.read_csv("data/processed/faculty_search_ready.csv")
    return df


@st.cache_resource

def load_models():
    vectorizer = joblib.load("tfidf_vectorizer.pkl")
    faculty_vectors = joblib.load("faculty_vectors.pkl")
    return vectorizer, faculty_vectors


df = load_data()
vectorizer, faculty_vectors = load_models()

# --------------------------------------------------
# Search box
# --------------------------------------------------
query = st.text_input(
    "Enter your research query:",
    placeholder="e.g. machine learning healthcare, blockchain security"
)

# Sidebar options
st.sidebar.header("Search Settings")
num_results = st.sidebar.slider("Number of Results", 1, 10, 5)
show_match_text = st.sidebar.checkbox("Show Matched Text", value=False)

# --------------------------------------------------
# Search logic
# --------------------------------------------------
if query:
    query_vector = vectorizer.transform([query])
    similarity_scores = cosine_similarity(
        query_vector,
        faculty_vectors
    ).flatten()

    top_indices = similarity_scores.argsort()[::-1][:num_results]

    st.subheader("Top Matching Faculty")

    found_any = False

    for idx in top_indices:
        score = float(similarity_scores[idx])

        if score <= 0:
            continue

        found_any = True
        row = df.iloc[idx]

        with st.container():
            st.markdown("---")

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"### {row['Name']}")
                st.write(f"**Designation:** {row['Designation']}")

            with col2:
                st.metric("Match Score", f"{score:.3f}")

            if pd.notna(row.get("WebsiteExpertise")) and str(row["WebsiteExpertise"]) != "nan" and str(row["WebsiteExpertise"]).strip() != "":
                st.write("**Website Expertise:**")
                st.info(row["WebsiteExpertise"])

            if pd.notna(row.get("ScholarExpertise")) and str(row["ScholarExpertise"]) != "nan" and str(row["ScholarExpertise"]).strip() != "":
                st.write("**Scholar Expertise:**")
                st.success(row["ScholarExpertise"])

            if show_match_text:
                st.write("**Matched Searchable Text:**")
                st.code(str(row["Searchable_Text"])[:700])

            if pd.notna(row.get("Bio")) and str(row["Bio"]).strip() != "":
                short_bio = str(row["Bio"])[:250]
        
            if len(str(row["Bio"])) > 250:
                short_bio = short_bio.rsplit(" ", 1)[0] + "..."
                
                st.write("**About:**")
                st.caption(short_bio)
                
        if not found_any:
            st.warning("No matching faculty found for this query.")

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.caption("Built using weighted expertise + TF-IDF + cosine similarity")