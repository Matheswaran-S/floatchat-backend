import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS (for frontend React/JS calls)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data from Excel
df = pd.read_excel("app/argo_dummy.xlsx")

@app.get("/")
def read_root():
    return {"message": "Welcome to FloatChat Backend with Excel data!"}


# Structured API endpoint
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
        "latitude": nearest["latitude"],
        "longitude": nearest["longitude"],
        "depth": nearest["depth"],
        "parameter": parameter,
        "value": nearest[parameter],
        "timestamp": str(nearest["timestamp"])
    }


# Natural language model
class QueryRequest(BaseModel):
    question: str


def handle_question(question: str):
    q = question.lower()

    parameter = "temperature"
    depth = 0
    lat, lon = 0, 0

    # Parameter detection
    if "salinity" in q:
        parameter = "salinity"
    elif "pressure" in q:
        parameter = "pressure"
    elif "temperature" in q:
        parameter = "temperature"

    # Ocean detection
    if "pacific" in q:
        lat, lon = 0, -160
    elif "indian" in q:
        lat, lon = -20, 80
    elif "atlantic" in q:
        lat, lon = 0, -30

    # Depth detection
    if "100m" in q or "100 m" in q:
        depth = 100
    elif "500m" in q or "500 m" in q:
        depth = 500

    # Find nearest record
    nearest = df.iloc[((df["latitude"] - lat).abs() +
                       (df["longitude"] - lon).abs() +
                       (df["depth"] - depth).abs()).argmin()]

    return {
        "question": question,
        "parameter": parameter,
        "latitude": nearest["latitude"],
        "longitude": nearest["longitude"],
        "depth": nearest["depth"],
        "value": nearest[parameter],
        "timestamp": str(nearest["timestamp"])
    }


# POST endpoint
@app.post("/ask")
def ask_query(req: QueryRequest):
    return handle_question(req.question)


# GET endpoint (browser/React-friendly)
@app.get("/ask")
def ask_get(query: str = Query(..., description="Natural language query")):
    return handle_question(query)


# Path-style endpoint
@app.get("/q/{text:path}")
def ask_path(text: str):
    return handle_question(text)











