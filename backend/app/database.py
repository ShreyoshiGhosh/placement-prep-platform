import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from sqlmodel import create_engine, Session  #we are using sqlmodel directly instead of creating supabase client because supabase client is messier when handling join queeries which we do have in this project but this was not the case in the e-permit system

load_dotenv(dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is missing")

engine = create_engine(DATABASE_URL, echo = True)

def get_db():
    with Session(engine) as session:
        yield session 