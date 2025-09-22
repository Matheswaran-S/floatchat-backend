import re
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow frontend (React, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset (Excel)
df = pd.read_excel("app/argo_dummy.xlsx")

@app.get("/")
def read_root():
    return {"message": "Welcome to FloatChat Backend with Excel data!"}

@app.get("/get_data")
def get_data(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    depth: float = Query(..., description="Depth in meters"),
    parameter: str = Query("temperature", description="Parameter: temperature, salinity, pressure")
):
    if parameter not in df.columns:
        return {"error": f"Invalid parameter. Choose from: {list(df.columns)}"}

    nearest = df.iloc[((df["latitude"] - lat).abs() +
                       (df["longitude"] - lon).abs() +
                       (df["depth"] - depth).abs()).argmin()]

    return {
        "latitude": float(nearest["latitude"]),
        "longitude": float(nearest["longitude"]),
        "depth": float(nearest["depth"]),
        "parameter": parameter,
        "value": float(nearest[parameter]),
        "timestamp": str(nearest["timestamp"])
    }

class QueryRequest(BaseModel):
    question: str

def process_question(q: str):
    q = q.lower()
    parameter, depth, lat, lon = "temperature", 0, None, None

    # Parameter detection
    if "salinity" in q:
        parameter = "salinity"
    elif "pressure" in q:
        parameter = "pressure"
    elif "temperature" in q:
        parameter = "temperature"

    # Depth extraction: match any number followed by "m"
    match = re.search(r'(\d+)\s*m', q)
    if match:
        depth = float(match.group(1))
    else:
        depth = 0  # Default if no depth is found

    # Extended region keywords with approximate lat/lon
    region_coords = {
        "south india beach": (8.5, 77.0),
        "bay of bengal": (15.0, 90.0),
        "middle of bay of bengal": (15.0, 90.0),
        "chennai beach": (13.0, 80.3),
        "goa beach": (15.4, 73.8),
        "arabian sea": (15.0, 65.0),
        "maldives": (3.2, 73.2),
        # add more regions as needed
    }

    # Check for matching region keywords in query
    for region, (r_lat, r_lon) in region_coords.items():
        if region in q:
            lat, lon = r_lat, r_lon
            break

    # Fallback to ocean-level rough locations if no region matched
    if lat is None or lon is None:
        if "pacific" in q:
            lat, lon = 0, -160
        elif "indian" in q:
            lat, lon = -20, 80
        elif "atlantic" in q:
            lat, lon = 0, -30

    # If still no coordinates found, reply with an error message
    if lat is None or lon is None:
        return {
            "question": q,
            "answer": "Sorry, I could not determine the ocean or region from your query. Try mentioning a known ocean or coastal region."
        }

    # Find the nearest datapoint in dataframe with respect to lat, lon, depth
    nearest = df.iloc[((df["latitude"] - lat).abs() +
                       (df["longitude"] - lon).abs() +
                       (df["depth"] - depth).abs()).argmin()]

    return {
        "question": q,
        "parameter": parameter,
        "latitude": float(nearest["latitude"]),
        "longitude": float(nearest["longitude"]),
        "depth": float(nearest["depth"]),
        "value": float(nearest[parameter]),
        "timestamp": str(nearest["timestamp"])
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

# Universal catch-all to support freeform query urls without 404
@app.get("/{text:path}")
def catch_all_get(text: str):
    question = text.replace("%20", " ")
    return process_question(question)













