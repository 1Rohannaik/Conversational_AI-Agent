from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.orchestrator import run_flow
from services.conversational_interview import handle_conversational_interview

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
        # Check if this is part of an ongoing conversation
        if req.conversation_session_id:
            # Handle as conversation continuation
            result = await handle_conversational_interview(
                file_id=str(req.file_id),
                user_input=req.question,
                session_id=req.conversation_session_id
            )
            
            # Return in flow format
            return {
                "intent": "conversation_continue",
                "answer": result["response"],
                "conversation_session_id": result.get("session_id"),
                "conversation_state": result.get("state"),
                "requires_response": result.get("requires_response", False),
                "progress": result.get("progress")
            }
        else:
            # Regular flow handling - pass conversation session ID if available
            result = await run_flow(
                str(req.file_id), 
                req.question, 
                conversation_session_id=req.conversation_session_id
            )
            
            # Check if this started a new conversation
            if result.get("intent") == "interview_start" and result.get("conversation_session_id"):
                result["requires_response"] = True
                result["conversation_state"] = "waiting_for_focus"
            
            return result
            
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run flow: {e}")
