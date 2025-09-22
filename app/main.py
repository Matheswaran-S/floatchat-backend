import random
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS (fixed warning issue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # change ["*"] to ["http://localhost:3000"] for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data from Excel file
try:
    df = pd.read_excel("app/argo_dummy.xlsx")
except Exception as e:
    print("Warning: Could not load Excel file:", e)
    df = pd.DataFrame(columns=["temperature", "salinity", "pressure", "depth", "latitude", "longitude", "timestamp"])

# ------------------------
# Root endpoint
# ------------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to FloatChat Backend with Excel + Natural Language support!"}

# ------------------------
# Structured API endpoint
# ------------------------
@app.get("/get_data")
def get_data(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    depth: float = Query(..., description="Depth in meters"),
    parameter: str = Query("temperature", description="Parameter: temperature, salinity, pressure")
):
    if parameter not in df.columns:
        return {"error": f"Invalid parameter. Choose from: {list(df.columns)}"}

    if df.empty:
        # Return realistic fallback if no data
        return {
            "latitude": lat,
            "longitude": lon,
            "depth": depth,
            "parameter": parameter,
            "value": round(random.uniform(1, 30), 2),
            "timestamp": "N/A (simulated)"
        }

    # Find nearest data point
    nearest = df.iloc[((df["latitude"] - lat).abs() +
                       (df["longitude"] - lon).abs() +
                       (df["depth"] - depth).abs()).argmin()]

    value = nearest[parameter]
    return {
        "latitude": nearest["latitude"],
        "longitude": nearest["longitude"],
        "depth": nearest["depth"],
        "parameter": parameter,
        "value": value,
        "timestamp": str(nearest["timestamp"])
    }

# ------------------------
# Natural Language API
# ------------------------
class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_query(req: QueryRequest):
    q = req.question.lower()

    # Defaults
    parameter = "temperature"
    depth = 0
    lat, lon = 0, 0

    # Detect parameter
    if "salinity" in q:
        parameter = "salinity"
    elif "pressure" in q:
        parameter = "pressure"
    elif "temperature" in q or "temp" in q:
        parameter = "temperature"

    # Ocean keywords → rough coordinates
    if "pacific" in q:
        lat, lon = 0, -160
    elif "indian" in q:
        lat, lon = -20, 80
    elif "atlantic" in q:
        lat, lon = 0, -30
    elif "arctic" in q:
        lat, lon = 80, 0
    elif "southern" in q:
        lat, lon = -60, 0

    # Extract depth from question if mentioned
    for d in [50, 100, 200, 500, 1000]:
        if f"{d}" in q:
            depth = d
            break

    # Handle explicit latitude/longitude
    if "latitude" in q or "lat" in q:
        try:
            lat = float(q.split("latitude")[-1].split()[0])
        except:
            pass
    if "longitude" in q or "lon" in q:
        try:
            lon = float(q.split("longitude")[-1].split()[0])
        except:
            pass

    # ------------------------
    # Get nearest match or fallback
    # ------------------------
    if df.empty:
        value = round(random.uniform(1, 30), 2)
        return {
            "question": req.question,
            "parameter": parameter,
            "latitude": lat,
            "longitude": lon,
            "depth": depth,
            "value": value,
            "timestamp": "N/A (simulated)"
        }

    nearest = df.iloc[((df["latitude"] - lat).abs() +
                       (df["longitude"] - lon).abs() +
                       (df["depth"] - depth).abs()).argmin()]
    value = nearest[parameter]

    return {
        "question": req.question,
        "parameter": parameter,
        "latitude": nearest["latitude"],
        "longitude": nearest["longitude"],
        "depth": nearest["depth"],
        "value": value,
        "timestamp": str(nearest["timestamp"])
    }










