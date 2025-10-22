"""
Orchestrator Service - Main Conversation Flow Controller (simplified)

Direct, dependency-light router that coordinates between services:
- Intent Classification
- Interview Engine (Hybrid RAG + Generative)
- Summary Engine
- RAG Pipeline
"""

from typing import Dict, Any, Optional, List
from .intent_classifier import classify_intent
from .interview_engine import InterviewEngine
from .summary_engine import SummaryEngine
from .rag_pipeline import aask_question
from .llm import get_llm_response

# In-memory storage for recent user questions (last 5)
recent_questions: List[str] = []

def add_question_to_history(question: str) -> None:
    """Add a question to the recent questions history (max 5)."""
    global recent_questions
    recent_questions.append(question)
    # Keep only the last 5 questions
    if len(recent_questions) > 5:
        recent_questions = recent_questions[-5:]

def get_recent_questions() -> List[str]:
    """Get the list of recent questions."""
    return recent_questions.copy()

def check_for_previous_question_intent(question: str) -> Optional[str]:
    """Check if user is asking about previous questions using LLM intelligence."""
    if not recent_questions:
        return None
    
    # Create context for LLM to understand the intent
    recent_questions_context = "\n".join([f"{i+1}. {q}" for i, q in enumerate(recent_questions)])
    
    # LLM prompt to intelligently detect if user wants previous questions
    intent_prompt = f"""
    User's current question: "{question}"
    
    Recent conversation history:
    {recent_questions_context}
    
    Task: Determine if the user is asking about their previous questions, conversation history, or what they asked before.
    
    Respond with ONLY one of these options:
    - "YES" if they're asking about previous questions/history
    - "NO" if they're asking something else
    
    Examples of YES cases:
    - "What did I ask before?"
    - "Can you remind me what I asked?"
    - "What was my previous question?"
    - "Show me my chat history"
    - "What questions have I asked?"
    
    Response:"""
    
    try:
        # Use LLM to determine intent
        llm_response = get_llm_response(intent_prompt)
        
        if "YES" in llm_response.upper():
            if len(recent_questions) == 1:
                return f"Your previous question was: '{recent_questions[-1]}'"
            else:
                return f"Your recent questions were:\n{recent_questions_context}"
    except Exception as e:
        # Fallback to None if LLM fails
        print(f"LLM intent detection failed: {e}")
        return None
    
    return None


async def run_flow(file_id: str, question: str, conversation_session_id: Optional[str] = None) -> Dict[str, Any]:
    """Main entry point for conversation orchestration (no LangGraph)."""
    
    # Check if user is asking about previous questions
    previous_question_response = check_for_previous_question_intent(question)
    if previous_question_response:
        return {
            "intent": "previous_questions",
            "answer": previous_question_response,
            "conversation_session_id": conversation_session_id
        }
    
    # Add current question to history before processing
    add_question_to_history(question)
    
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
