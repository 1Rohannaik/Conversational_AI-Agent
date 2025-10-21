from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.conversational_interview import handle_conversational_interview, get_conversation_status


router = APIRouter(prefix="/conversation", tags=["Conversational Interview"])


class ConversationRequest(BaseModel):
    file_id: int
    user_input: str
    session_id: Optional[str] = None


@router.post("/interview")
async def continue_conversation(req: ConversationRequest):
    """Continue or start a conversational interview session."""
    if not req.user_input or not req.user_input.strip():
        raise HTTPException(status_code=400, detail="User input cannot be empty")
    
    try:
        result = await handle_conversational_interview(
            file_id=str(req.file_id),
            user_input=req.user_input,
            session_id=req.session_id
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process conversation: {e}")


@router.get("/status/{session_id}")
async def get_conversation_session_status(session_id: str):
    """Get the status of a conversational interview session."""
    try:
        status = get_conversation_status(session_id)
        if not status:
            raise HTTPException(status_code=404, detail="Session not found")
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {e}")