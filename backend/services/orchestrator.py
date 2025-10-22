"""
Orchestrator Service - Main Conversation Flow Controller (simplified)

Direct, dependency-light router that coordinates between services:
- Intent Classification
- Interview Engine (Hybrid RAG + Generative)
- Summary Engine
- RAG Pipeline
"""

from typing import Dict, Any, Optional
from .intent_classifier import classify_intent
from .interview_engine import InterviewEngine
from .summary_engine import SummaryEngine
from .rag_pipeline import aask_question


async def run_flow(file_id: str, question: str, conversation_session_id: Optional[str] = None) -> Dict[str, Any]:
    """Main entry point for conversation orchestration (no LangGraph)."""
    intent = await classify_intent(question, conversation_session_id)

    # Route to the appropriate flow
    if intent == "summary":
        result = await SummaryEngine.generate_summary(file_id, question)
    elif intent == "interview":
        result = await InterviewEngine.start_interview(file_id, question)
    elif intent == "interview_continue":
        # Preserve existing session id in the response
        result = await InterviewEngine.continue_interview(file_id, user_answer=question, document_analysis="")
        if conversation_session_id:
            result["conversation_session_id"] = conversation_session_id
    elif intent == "end_interview":
        result = await InterviewEngine.end_interview(file_id)
        # Ensure session is cleared
        result["conversation_session_id"] = None
    else:
        # Default to RAG
        answer = await aask_question(file_id, question)
        result = {"intent": "rag", "answer": answer}

    # Standardize response payload
    response: Dict[str, Any] = {
        "intent": result.get("intent"),
        "answer": result.get("answer"),
    }
    if result.get("conversation_session_id") is not None:
        response["conversation_session_id"] = result.get("conversation_session_id")
    if result.get("requires_response") is not None:
        response["requires_response"] = result.get("requires_response")
    if result.get("conversation_state") is not None:
        response["conversation_state"] = result.get("conversation_state")

    return response
