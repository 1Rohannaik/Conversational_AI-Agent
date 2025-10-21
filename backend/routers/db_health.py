from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db, ping


router = APIRouter(prefix="/db", tags=["db"])


@router.get("/health")
def db_health() -> dict:
    # Raises on failure
    ping()
    return {"status": "ok"}


@router.get("/ping")
def db_ping(db: Session = Depends(get_db)) -> dict:
    # Just opening a session validates connection; ping() executes a lightweight query
    ping()
    return {"ping": 1}
