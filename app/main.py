from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

# Path to your CSV/XLSX file
FILE_PATH = os.path.join("app", "argo_dummy.csv")  # or "argo_dummy.xlsx"

# Load the data
try:
    if FILE_PATH.endswith(".csv"):
        df = pd.read_csv(FILE_PATH)
    else:
        df = pd.read_excel(FILE_PATH)
except Exception as e:
    print(f"Error loading file: {e}")
    df = pd.DataFrame()  # empty dataframe as fallback

# Create FastAPI app
app = FastAPI()

# Enable CORS for frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {"message": "Hello from backend deployed on Render!"}

# Generic endpoint to get row by depth or index
@app.get("/data")
def get_data(depth: float = None, index: int = None):
    """
    Retrieve data by depth (if column 'depth' exists) or by row index.
    """
    if df.empty:
        raise HTTPException(status_code=500, detail="Data file not loaded")

    # If depth is provided and column exists
    if depth is not None and "depth" in df.columns:
        row = df[df["depth"] == depth]
        if row.empty:
            raise HTTPException(status_code=404, detail="Depth not found")
        return row.to_dict(orient="records")[0]

    # If index is provided
    if index is not None:
        if index < 0 or index >= len(df):
            raise HTTPException(status_code=404, detail="Index out of range")
        return df.iloc[index].to_dict()

    # If nothing provided, return entire dataset
    return df.to_dict(orient="records")

# Example: get temperature at a specific depth if CSV has 'temperature' column
@app.get("/temperature")
def get_temperature(depth: float):
    if df.empty or "temperature" not in df.columns or "depth" not in df.columns:
        raise HTTPException(status_code=500, detail="Temperature or depth data not available")

    row = df[df["depth"] == depth]
    if row.empty:
        raise HTTPException(status_code=404, detail="Depth not found")

    temp = row["temperature"].values[0]
    return {"depth": f"{depth}m", "temperature": f"{temp}°C"}

# Example: get salinity at a specific depth if CSV has 'salinity' column
@app.get("/salinity")
def get_salinity(depth: float):
    if df.empty or "salinity" not in df.columns or "depth" not in df.columns:
        raise HTTPException(status_code=500, detail="Salinity or depth data not available")

    row = df[df["depth"] == depth]
    if row.empty:
        raise HTTPException(status_code=404, detail="Depth not found")

    salinity = row["salinity"].values[0]
    return {"depth": f"{depth}m", "salinity": f"{salinity} PSU"}
