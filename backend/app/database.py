import os
# pyrefly: ignore [missing-import] 
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from sqlmodel import create_engine, Session  #we are using sqlmodel directly instead of creating supabase client because supabase client is messier when handling join queeries which we do have in this project but this was not the case in the e-permit system

load_dotenv(dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL: #if the database url is not found ? what uf theres a dummy variable in place of the database url?? will this error be raised? what is ValueError? whats its purpose just an alert or does it do sometjjhing more than that?
    raise ValueError("DATABASE_URL environment variable is missing") # will the next line run if an error is raised? i basiscally donot have good knowledge about errors so imma need your help

try:
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        pool_pre_ping=True
    )

    with engine.connect() as conn:
        print("Database connection successful")

except Exception as e:
    raise RuntimeError(
        f"Database startup failed: {e}"
    )

def get_db(): # i neither understadn the syntax nor do i understand the whats session? and what is it exactly doing???
    with Session(engine) as session: 
        yield session 