from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI()

# Allow frontend (React) to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict to specific domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {"message": "Hello from backend deployed on Render!"}

# Example API endpoint (for testing)
@app.get("/temperature")
def get_temperature(depth: int = 100):
    # Mock response for now
    return {"depth": depth, "temperature": "25°C"}
