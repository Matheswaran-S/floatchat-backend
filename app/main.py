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

    # Map Excel column names to API expected columns
    column_mapping = {
        "latitude": "lat",
        "longitude": "long",
        "datetime": "time",
        "temperature": "temperature",  # fix typo in Excel
        "salinity": "salinity",
        "pressure": "pressure"
    }

    df = df.rename(columns=column_mapping)

except Exception as e:
    print(f"Error loading file: {e}")
    df = pd.DataFrame()

# -------------------------
# Create FastAPI app
# -------------------------
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all domains
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
# Return all available depths
# -------------------------
@app.get("/depths")
def get_depths():
    if df.empty or "depth" not in df.columns:
        raise HTTPException(status_code=500, detail="Depth data not available")
    return {"depths": df["depth"].tolist()}


# -------------------------
# Generic function to get values by depth
# -------------------------
def get_value_by_depth(column: str, depth: float):
    if df.empty or column not in df.columns or "depth" not in df.columns:
        raise HTTPException(status_code=500, detail=f"{column} or depth data not available")

    row = df[df["depth"] == depth]
    if row.empty:
        random_row = df.sample(1).iloc[0]
        return random_row[column], True
    return row[column].values[0], False


# -------------------------
# Temperature by depth
# -------------------------
@app.get("/temperature")
def get_temperature(depth: float):
    value, is_random = get_value_by_depth("temperature", depth)
    response = {"depth": depth, "temperature": value}
    if is_random:
        response["note"] = "Random data returned, depth not found"
    return response


# -------------------------
# Salinity by depth
# -------------------------
@app.get("/salinity")
def get_salinity(depth: float):
    value, is_random = get_value_by_depth("salinity", depth)
    response = {"depth": depth, "salinity": value}
    if is_random:
        response["note"] = "Random data returned, depth not found"
    return response


# -------------------------
# Pressure by depth
# -------------------------
@app.get("/pressure")
def get_pressure(depth: float):
    value, is_random = get_value_by_depth("pressure", depth)
    response = {"depth": depth, "pressure": value}
    if is_random:
        response["note"] = "Random data returned, depth not found"
    return response


# -------------------------
# Argo data by lat, long, time
# -------------------------
@app.get("/argo-data")
def get_argo_data(
        lat: float = Query(..., description="Latitude"),
        long: float = Query(..., description="Longitude"),
        time: str = Query(..., description="Time in YYYY-MM-DD format")
):
    required_columns = ["lat", "long", "time", "temperature", "salinity", "pressure"]
    if df.empty or not all(col in df.columns for col in required_columns):
        raise HTTPException(status_code=500, detail="Required data columns not available")

    # Filter by lat, long, time
    row = df[
        (df["lat"] == lat) &
        (df["long"] == long) &
        (df["time"] == time)
        ]

    if row.empty:
        random_row = df.sample(1).iloc[0]
        return {
            "lat": lat,
            "long": long,
            "time": time,
            "temperature": random_row["temperature"],
            "salinity": random_row["salinity"],
            "pressure": random_row["pressure"],
            "note": "Random data returned, coordinates/time not found"
        }

    return row.to_dict(orient="records")[0]




