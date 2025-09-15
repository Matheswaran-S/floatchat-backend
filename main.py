from fastapi import FastAPI
from app.routes import mock   # import mock router

app = FastAPI(title="FloatChat Backend")

# include mock routes
app.include_router(mock.router)

@app.get("/")
def read_root():
    return {"message": "Hello, FloatChat is running 🚀"}
