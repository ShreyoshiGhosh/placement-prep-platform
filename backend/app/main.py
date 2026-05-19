from fastapi import FastAPI, Depends
# pyrefly: ignore [missing-import]
from sqlmodel import Session, text
from app.database import get_db

app = FastAPI(
    title = "Placement Prep Platform",
    description = "Backend API for adaptive aptitude and reasoning practice",
    version = "1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Placement Prep Platform API"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return { "status": "healthy", "database": "connected"}
    except Exception as e:
        return { "status": "unhealthy", "database": "disconnected", "error": str(e)}