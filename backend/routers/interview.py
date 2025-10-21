from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from services.interview import start_interview, submit_answer, get_status


router = APIRouter(prefix="/interview", tags=["Interview"])


class StartRequest(BaseModel):
    file_id: int
    num_questions: int = Field(5, ge=1, le=10)
    focus: Optional[str] = None
    level: Optional[str] = Field(None, description="e.g., junior, mid, senior")


@router.post("/start")
async def start(req: StartRequest):
    try:
        return await start_interview(str(req.file_id), req.num_questions, req.focus, req.level)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {e}")


class AnswerRequest(BaseModel):
    session_id: str
    answer: str


@router.post("/answer")
async def answer(req: AnswerRequest):
    if not req.answer or not req.answer.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty")
    try:
        return await submit_answer(req.session_id, req.answer)
    except KeyError as ke:
        raise HTTPException(status_code=404, detail=str(ke))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process answer: {e}")


@router.get("/status/{session_id}")
async def status(session_id: str):
    try:
        return get_status(session_id)
    except KeyError as ke:
        raise HTTPException(status_code=404, detail=str(ke))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {e}")
