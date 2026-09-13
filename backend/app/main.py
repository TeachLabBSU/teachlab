from fastapi import FastAPI
from app.routers import users

app = FastAPI(
    title="TeachLab API",
    description="Backend TeachLab",
    version="0.1.0"
)

app.include_router(users.router)

@app.get("/")
def root():
    return {
        "project": "TeachLab",
        "status": "running",
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}