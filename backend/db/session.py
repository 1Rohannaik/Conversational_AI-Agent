import os
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


# Load environment variables from .env if present
load_dotenv()

# Read DATABASE_URL from env; fall back to the provided example if missing
DATABASE_URL = os.getenv("DATABASE_URL")


# Create SQLAlchemy engine (synchronous)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
