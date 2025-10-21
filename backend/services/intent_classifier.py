"""
Intent Classification Service

Handles keyword-based intent classification for the conversational AI system.
Supports interview flows, document summarization, and RAG queries.
"""

from typing import Optional


async def classify_intent(question: str, conversation_session_id: Optional[str] = None) -> str:
    """Enhanced keyword-based intent classification with interview detection."""
    
    question_lower = question.lower()
    
    # Check for interview termination FIRST (before session check)
    end_keywords = [
        'end interview', 'stop interview', 'finish interview', 
        'exit interview', 'done with interview', 'end this', 'stop this'
    ]
    if any(keyword in question_lower for keyword in end_keywords):
        return "end_interview"
    
    # If we have a conversation session ID, this is likely an interview continuation
    if conversation_session_id:
        return "interview_continue"
    
    # Enhanced interview detection with more patterns
    interview_keywords = [
        'interview', 'take my interview', 'interview me', 'start interview', 
        'ask me questions', 'conduct interview', 'begin interview',
        'quiz me', 'test my knowledge', 'assess me', 'evaluate me',
        'practice interview', 'mock interview', 'job interview'
    ]
    if any(keyword in question_lower for keyword in interview_keywords):
        return "interview"
    
    # Check for summary keywords
    summary_keywords = [
        'summary', 'summarize', 'synopsis', 'overview', 'brief', 
        'main points', 'key points', 'outline'
    ]
    if any(keyword in question_lower for keyword in summary_keywords):
        return "summary"
    
    # Default to RAG for everything else
    return "rag"


def get_supported_intents():
    """Return list of all supported intents."""
    return [
        "interview",
        "interview_continue", 
        "end_interview",
        "summary",
        "rag"
    ]