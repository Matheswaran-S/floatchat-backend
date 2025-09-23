import re
import json
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import dateparser
from datetime import datetime, timedelta
from rapidfuzz import process, fuzz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset
df = pd.read_excel("app/argo_dummy.xlsx")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Load locations from JSON file
with open("app/locations.json", "r", encoding="utf-8") as f:
    locations_list = json.load(f)

location_names = [loc["name"] for loc in locations_list]

class QueryRequest(BaseModel):
    question: str

def find_location_fuzzy(query: str, threshold=75):
    best_match = process.extractOne(query, location_names, scorer=fuzz.partial_ratio)
    if best_match and best_match[1] >= threshold:
        matched_name = best_match[0]
        for loc in locations_list:
            if loc["name"] == matched_name:
                return loc["latitude"], loc["longitude"]
    return None, None

def process_question(q: str):
    q_lower = q.lower().strip()

    # Return early if question empty or only whitespace
    if not q_lower:
        return {
            "question": "",
            "answer": "Please provide a location or query to get data about ocean, sea, coast, or beach."
        }

    # Detect parameters requested (support multiple)
    parameters = []
    if "temperature" in q_lower:
        parameters.append("temperature")
    if "pressure" in q_lower:
        parameters.append("pressure")
    if "salinity" in q_lower:
        parameters.append("salinity")

    # Default parameter if none found
    if not parameters:
        parameters = ["temperature"]  # default to temperature

    # Extract depth (number followed by 'm')
    depth_match = re.search(r'(\d+)\s*m', q_lower)
    depth = float(depth_match.group(1)) if depth_match else 0

    # Parse date/time using dateparser
    dt = dateparser.parse(q_lower, settings={'PREFER_DATES_FROM': 'past'})
    if dt is not None:
        display_timestamp = dt
    else:
        display_timestamp = datetime.now() - timedelta(minutes=10)

    # Find location using fuzzy matching
    lat, lon = find_location_fuzzy(q_lower)
    if lat is None or lon is None:
        return {
            "question": q,
            "answer": "Sorry, I could not determine the ocean, sea, coast, or beach from your query. Please specify a known coastal or oceanic location."
        }

    # Find nearest data point by lat, lon, depth
    nearest = df.iloc[((df["latitude"] - lat).abs() +
                       (df["longitude"] - lon).abs() +
                       (df["depth"] - depth).abs()).argmin()]

    # Build response values object for all requested parameters
    values = {}
    for param in parameters:
        values[param] = float(nearest[param])

    return {
        "question": q,
        "location": {
            "latitude": float(nearest["latitude"]),
            "longitude": float(nearest["longitude"]),
            "depth": float(nearest["depth"])
        },
        "values": values,
        "timestamp": display_timestamp.isoformat()
    }

@app.post("/ask")
def ask_post(req: QueryRequest):
    return process_question(req.question)

@app.get("/ask")
def ask_get(query: str = Query(..., description="Natural language query")):
    return process_question(query)

@app.get("/query")
def query_get(text: str = Query(..., description="Natural language query")):
    return process_question(text)

@app.get("/{text:path}")
def catch_all_get(text: str):
    question = text.replace("%20", " ")
    return process_question(question)















