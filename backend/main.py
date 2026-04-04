from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import os
from typing import List, Optional
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
from google.genai import types
from dotenv import load_dotenv
# Load environment variables from .env file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, "backend", ".env")
load_dotenv(ENV_PATH, override=True)

app = FastAPI()

# Enable CORS for React frontend (usually runs on port 5173 or 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Load data + saved TF-IDF objects
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "faculty_search_ready.csv")
VECTORIZER_PATH = os.path.join(BASE_DIR, "tfidf_vectorizer.pkl")
VECTORS_PATH = os.path.join(BASE_DIR, "faculty_vectors.pkl")

try:
    df = pd.read_csv(DATA_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    faculty_vectors = joblib.load(VECTORS_PATH)
    print("Models and data loaded successfully.")
except Exception as e:
    print(f"Error loading models or data: {e}")
    # Initialize empty if files not found during development
    df = pd.DataFrame()
    vectorizer = None
    faculty_vectors = None

# Initialize Gemini Client (v1 SDK)
# Using GOOGLE_API_KEY as it's the standard for the new SDK
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

class QueryRequest(BaseModel):
    query: str
    num_results: int = 5

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    query: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "MIT Faculty AI Backend (Gemini v1) is running"}

@app.post("/search")
async def search(request: QueryRequest):
    if vectorizer is None or faculty_vectors is None or df.empty:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    query_vector = vectorizer.transform([request.query])
    similarity_scores = cosine_similarity(query_vector, faculty_vectors).flatten()
    
    top_indices = similarity_scores.argsort()[::-1][:request.num_results]
    
    results = []
    for idx in top_indices:
        score = float(similarity_scores[idx])
        if score <= 0:
            continue
        
        row = df.iloc[idx]
        results.append({
            "name": str(row["Name"]),
            "designation": str(row["Designation"]),
            "score": score,
            "website_expertise": str(row.get("WebsiteExpertise", "")),
            "scholar_expertise": str(row.get("ScholarExpertise", "")),
            "bio": str(row.get("Bio", ""))[:500] if pd.notna(row.get("Bio")) else ""
        })
    
    return {"results": results}

@app.post("/chat")
async def chat(request: ChatRequest):
    # 1. Perform search based on the last user message if no explicit query
    user_query = request.query or (request.messages[-1].content if request.messages else "")
    
    faculty_results = []
    context = ""
    if user_query and vectorizer is not None:
        query_vector = vectorizer.transform([user_query])
        similarity_scores = cosine_similarity(query_vector, faculty_vectors).flatten()
        top_indices = similarity_scores.argsort()[::-1][:5] # Top 5 for better coverage
        
        for idx in top_indices:
            score = float(similarity_scores[idx])
            if score > 0:
                row = df.iloc[idx]
                faculty_results.append({
                    "name": str(row["Name"]),
                    "designation": str(row["Designation"]),
                    "score": score,
                    "website_expertise": str(row.get("WebsiteExpertise", "")),
                    "scholar_expertise": str(row.get("ScholarExpertise", "")),
                    "bio": str(row.get("Bio", ""))[:500] if pd.notna(row.get("Bio")) else ""
                })
        
        if faculty_results:
            context_list = [f"- {f['name']} ({f['designation']}): {f['website_expertise']} {f['scholar_expertise']}" for f in faculty_results[:3]]
            context = "Relevant MIT Faculty Information:\n" + "\n".join(context_list)
    
    # 2. Build system instruction
    system_instruction = f"""You are MIT Faculty AI, a helpful assistant for finding MIT faculty members and their research. 
Help users find professors based on research areas, departments, expertise, publications, and contact info. 
Be concise, friendly, and accurate.

{context}

If faculty are found in the context, please confirm that you've found some relevant faculty and provide a brief summary. I will display the cards separately, so you don't need to list all their details in the text, just a helpful response."""

    # 3. Format history for new SDK
    contents = []
    for m in request.messages:
        role = "user" if m.role == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=m.content)]))

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=1000
            )
        )
        
        return {
            "reply": response.text,
            "faculty": faculty_results
        }
    except Exception as e:
        error_msg = str(e)
        print(f"Gemini API Error: {error_msg}")
        
        reply = "I found some faculty that might match your interest."
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            reply = "I found relevant faculty, but the AI Chat is currently hitting a rate limit (429). Please wait a few seconds and try again! Direct results are shown below."
        elif "API_KEY_INVALID" in error_msg:
            reply = "The Gemini API key provided seems to be invalid. Please check your .env file."
        
        if faculty_results:
            return {
                "reply": reply,
                "faculty": faculty_results
            }
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
