import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

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
        "latitude": nearest["latitude"],
        "longitude": nearest["longitude"],
        "depth": nearest["depth"],
        "parameter": parameter,
        "value": nearest[parameter],
        "timestamp": str(nearest["timestamp"])
    }

class QueryRequest(BaseModel):
    question: str

def process_question(q: str):
    q = q.lower()
    parameter, depth, lat, lon = "temperature", 0, None, None
    if "salinity" in q:
        parameter = "salinity"
    elif "pressure" in q:
        parameter = "pressure"
    elif "temperature" in q:
        parameter = "temperature"
    if "pacific" in q:
        lat, lon = 0, -160
    elif "indian" in q:
        lat, lon = -20, 80
    elif "atlantic" in q:
        lat, lon = 0, -30
    if "100m" in q or "100 m" in q:
        depth = 100
    elif "500m" in q or "500 m" in q:
        depth = 500

    if lat is None or lon is None:
        return {
            "question": q,
            "answer": "Sorry, I could not determine the ocean region from your query. Try mentioning Pacific, Indian, or Atlantic."
        }
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

# UNIVERSAL CATCH-ALL: any /something-else calls this
@app.get("/{text:path}")
def catch_all_get(text: str):
    # Drop leading / if present, decode %20 to space
    question = text.replace("%20", " ")
    return process_question(question)













