"""
Intent Classification Service

Handles intelligent LLM-based intent classification for the conversational AI system.
Supports interview flows, document summarization, and RAG queries.
"""

from typing import Optional
from .llm import get_llm_response


async def classify_intent(question: str, conversation_session_id: Optional[str] = None) -> str:
    """Enhanced LLM-based intent classification with fallback to keyword detection."""
    
    # If we have a conversation session ID, this is likely an interview continuation
    if conversation_session_id:
        # Use LLM to check if user wants to end the interview
        try:
            end_check_prompt = f"""
            User message: "{question}"
            
            The user is currently in an interview session. Determine if they want to END/STOP the interview.
            
            Respond with ONLY:
            - "END" if they want to stop/end/exit the interview
            - "CONTINUE" if they want to continue or are answering questions
            
            Examples of END:
            - "end interview", "stop this", "I'm done", "finish interview"
            
            Examples of CONTINUE:
            - Any answer to interview questions
            - "yes", "no", actual responses
            
            Response:"""
            
            llm_response = get_llm_response(end_check_prompt)
            if "END" in llm_response.upper():
                return "end_interview"
            else:
                return "interview_continue"
        except:
            # Fallback to keyword detection
            question_lower = question.lower()
            end_keywords = ['end interview', 'stop interview', 'finish interview', 'exit interview', 'done with interview', 'end this', 'stop this']
            if any(keyword in question_lower for keyword in end_keywords):
                return "end_interview"
            return "interview_continue"
    
    # Use LLM for intent classification
    try:
        intent_prompt = f"""
        User question: "{question}"
        
        Classify this question into ONE of these intents:
        
        1. INTERVIEW - User wants to start an interview, be interviewed, or be asked questions about a topic
        2. SUMMARY - User wants a summary, overview, or main points of content
        3. RAG - User has a specific question about content or wants information (default)
        
        Consider these patterns:
        
        INTERVIEW examples:
        - "Interview me about this topic"
        - "Ask me questions"
        - "Test my knowledge"
        - "Practice interview"
        - "Quiz me"
        
        SUMMARY examples:
        - "Summarize this document"
        - "Give me an overview"
        - "What are the main points?"
        - "Brief summary"
        
        RAG examples:
        - "What is...?"
        - "How does...?"
        - "Explain..."
        - "Tell me about..."
        
        Respond with ONLY: INTERVIEW, SUMMARY, or RAG
        
        Response:"""
        
        llm_response = get_llm_response(intent_prompt)
        intent = llm_response.strip().upper()
        
        if "INTERVIEW" in intent:
            return "interview"
        elif "SUMMARY" in intent:
            return "summary"
        else:
            return "rag"
            
    except Exception as e:
        print(f"LLM intent classification failed: {e}")
        # Fallback to keyword-based classification
        return await classify_intent_fallback(question)


async def classify_intent_fallback(question: str) -> str:
    """Fallback keyword-based intent classification."""
    question_lower = question.lower()
    
    # Enhanced interview detection
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