"""
Flow Manager Service

Manages the execution of different conversation flows including
interview, summary, and RAG-based question answering.
"""

from typing import Dict, Any
from .interview_engine import InterviewEngine
from .summary_engine import SummaryEngine
from .rag_pipeline import aask_question


class FlowManager:
    """Manages execution of different conversation flows."""
    
    @staticmethod
    async def run_interview_flow(state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute interview flow with hybrid RAG + generative approach."""
        file_id = str(state["file_id"])
        question = state["question"]
        
        result = await InterviewEngine.start_interview(file_id, question)
        
        # Update state with interview results
        state.update(result)
        return state
    
    @staticmethod
    async def run_interview_continue_flow(state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute interview continuation flow."""
        file_id = str(state["file_id"])
        user_answer = state["question"]
        document_analysis = state.get("document_analysis", "")
        
        result = await InterviewEngine.continue_interview(file_id, user_answer, document_analysis)
        
        # Preserve session information
        result["conversation_session_id"] = state.get("conversation_session_id")
        
        # Update state with continuation results
        state.update(result)
        return state
    
    @staticmethod
    async def run_end_interview_flow(state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute interview termination flow."""
        file_id = str(state["file_id"])
        
        result = await InterviewEngine.end_interview(file_id)
        
        # Update state with end results
        state.update(result)
        return state
    
    @staticmethod
    async def run_summary_flow(state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute document summary flow."""
        file_id = str(state["file_id"])
        question = state["question"]
        
        result = await SummaryEngine.generate_summary(file_id, question)
        
        # Update state with summary results
        state.update(result)
        return state
    
    @staticmethod
    async def run_rag_flow(state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute RAG-based question answering flow."""
        file_id = str(state["file_id"])
        question = state["question"]
        
        answer = await aask_question(file_id, question)
        
        state["answer"] = answer
        state["intent"] = "rag"
        return state