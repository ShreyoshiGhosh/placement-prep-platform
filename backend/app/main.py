
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, text

from app.database import get_db
from .routers import auth, users, quiz_engine
app = FastAPI(
    title = "Placement Prep Platform",
    description = "Backend API for adaptive aptitude and reasoning practice",
    version = "1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")
app.include_router(quiz_engine.router, prefix="/quiz_engine")