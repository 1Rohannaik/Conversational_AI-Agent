from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.orchestrator import run_flow

router = APIRouter(prefix="/flow", tags=["Flow"])


class FlowRequest(BaseModel):
    file_id: int
    question: str
    conversation_session_id: Optional[str] = None


@router.post("/ask")
async def ask_flow(req: FlowRequest):
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        # Process the request through the orchestrator
        result = await run_flow(
            str(req.file_id), 
            req.question, 
            conversation_session_id=req.conversation_session_id
        )
        return result
            
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run flow: {e}")
