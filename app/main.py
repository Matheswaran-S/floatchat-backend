from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

# Robust path: always relative to main.py
FILE_PATH = os.path.join(os.path.dirname(__file__), "argo_dummy.xlsx")

# Load the Excel file
try:
    df = pd.read_excel(FILE_PATH)  # read Excel
except Exception as e:
    print(f"Error loading file: {e}")
    df = pd.DataFrame()  # fallback to empty DataFrame

# Create FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {"message": "Hello from backend deployed on Render!"}

# Return all available depths
@app.get("/depths")
def get_depths():
    if df.empty or "depth" not in df.columns:
        raise HTTPException(status_code=500, detail="Depth data not available")
    return {"depths": df["depth"].tolist()}

# Get temperature by depth
@app.get("/temperature")
def get_temperature(depth: float):
    if df.empty or "temperature" not in df.columns or "depth" not in df.columns:
        raise HTTPException(status_code=500, detail="Temperature or depth data not available")
    row = df[df["depth"] == depth]
    if row.empty:
        raise HTTPException(status_code=404, detail="Depth not found")
    temp = row["temperature"].values[0]
    return {"depth": depth, "temperature": temp}

# Get salinity by depth
@app.get("/salinity")
def get_salinity(depth: float):
    if df.empty or "salinity" not in df.columns or "depth" not in df.columns:
        raise HTTPException(status_code=500, detail="Salinity or depth data not available")
    row = df[df["depth"] == depth]
    if row.empty:
        raise HTTPException(status_code=404, detail="Depth not found")
    salinity = row["salinity"].values[0]
    return {"depth": depth, "salinity": salinity}

