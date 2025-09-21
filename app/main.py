from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import random

# -------------------------
# Load Excel file robustly
# -------------------------
FILE_PATH = os.path.join(os.path.dirname(__file__), "argo_dummy.xlsx")

try:
    df = pd.read_excel(FILE_PATH)

    # Map Excel columns to API expected columns
    column_mapping = {
        "latitude": "lat",
        "longitude": "long",
        "datetime": "time",
        "temperatu": "temperature",
        "salinity": "salinity",
        "pressure": "pressure"
    }

    # Only rename columns that exist in the Excel
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

except Exception as e:
    print(f"Error loading file: {e}")
    df = pd.DataFrame()

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Root endpoint
# -------------------------
@app.get("/")
def root():
    return {"message": "Hello from backend deployed on Render!"}

# -------------------------
# Depth endpoints (robust)
# -------------------------
@app.get("/depths")
def get_depths():
    if df.empty:
        return {"depths": [], "note": "Data is empty"}
    if "depth" in df.columns:
        return {"depths": df["depth"].tolist()}
    else:
        sample_depths = [random.uniform(0, 1000) for _ in range(5)]
        return {"depths": sample_depths, "note": "Depth column missing, random values returned"}

def get_value_by_depth(column: str, depth: float):
    if df.empty or column not in df.columns:
        raise HTTPException(status_code=500, detail=f"{column} data not available")
    if "depth" not in df.columns:
        random_row = df.sample(1).iloc[0]
        return random_row[column], True
    row = df[df["depth"] == depth]
    if row.empty:
        random_row = df.sample(1).iloc[0]
        return random_row[column], True
    return row[column].values[0], False

@app.get("/temperature")
def get_temperature(depth: float):
    value, is_random = get_value_by_depth("temperature", depth)
    response = {"depth": depth, "temperature": value}
    if is_random:
        response["note"] = "Random data returned, depth not found or column missing"
    return response

@app.get("/salinity")
def get_salinity(depth: float):
    value, is_random = get_value_by_depth("salinity", depth)
    response = {"depth": depth, "salinity": value}
    if is_random:
        response["note"] = "Random data returned, depth not found or column missing"
    return response

@app.get("/pressure")
def get_pressure(depth: float):
    value, is_random = get_value_by_depth("pressure", depth)
    response = {"depth": depth, "pressure": value}
    if is_random:
        response["note"] = "Random data returned, depth not found or column missing"
    return response

# -------------------------
# Combined endpoint: temperature, salinity, pressure
# -------------------------
@app.get("/argo-full")
def get_argo_full(
    lat: float = Query(..., description="Latitude"),
    long: float = Query(..., description="Longitude"),
    time: str = Query(..., description="Time in YYYY-MM-DD format"),
    depth: float = Query(None, description="Optional depth")
):
    # Required columns check
    required_columns = ["lat", "long", "time", "temperature", "salinity", "pressure"]
    if df.empty or not all(col in df.columns for col in required_columns):
        raise HTTPException(status_code=500, detail="Required data columns not available")

    # Filter by lat, long, time
    row = df[
        (df["lat"] == lat) &
        (df["long"] == long) &
        (df["time"] == time)
    ]

    # If depth provided, further filter
    if depth is not None and "depth" in df.columns:
        row = row[row["depth"] == depth]

    # If no exact match, return random row
    if row.empty:
        random_row = df.sample(1).iloc[0]
        return {
            "lat": lat,
            "long": long,
            "time": time,
            "depth": depth if depth is not None else random_row.get("depth"),
            "temperature": random_row["temperature"],
            "salinity": random_row["salinity"],
            "pressure": random_row["pressure"],
            "note": "Random data returned, exact match not found"
        }

    # Return first matched row
    result = row.iloc[0]
    return {
        "lat": result["lat"],
        "long": result["long"],
        "time": result["time"],
        "depth": result.get("depth"),
        "temperature": result["temperature"],
        "salinity": result["salinity"],
        "pressure": result["pressure"]
    }






