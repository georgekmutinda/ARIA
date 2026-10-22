import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from collections.abc import Generator
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL =os.getenv(
    "DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is missing! Check your .env file.")


engine= create_engine(
    DATABASE_URL,
    pool_size = 10,
    max_overflow=20,
    pool_pre_ping=True,   
)

SessionLocal=sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()