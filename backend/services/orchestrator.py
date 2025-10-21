"""
Orchestrator Service - Main Conversation Flow Controller

Simplified orchestrator that coordinates between different services:
- Intent Classification
- Interview Engine (Hybrid RAG + Generative)
- Summary Engine
- Flow Manager
- RAG Pipeline

This modular approach separates concerns and makes the system more maintainable.
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END

from .intent_classifier import classify_intent
from .flow_manager import FlowManager


# Type alias for cleaner code
State = Dict[str, Any]


def _build_graph():
    """Build the LangGraph workflow for conversation orchestration."""
    graph = StateGraph(dict)

    async def classify_node(state: State) -> State:
        """Classify user intent based on question and conversation context."""
        intent = state.get("intent") or await classify_intent(
            state["question"], 
            state.get("conversation_session_id")
        )
        state["intent"] = intent
        return state

    # Add all nodes
    graph.add_node("classify", classify_node)
    graph.add_node("summary_flow", FlowManager.run_summary_flow)
    graph.add_node("interview_flow", FlowManager.run_interview_flow)
    graph.add_node("interview_continue_flow", FlowManager.run_interview_continue_flow)
    graph.add_node("end_interview_flow", FlowManager.run_end_interview_flow)
    graph.add_node("rag_flow", FlowManager.run_rag_flow)

    # Set entry point
    graph.set_entry_point("classify")

    def router(state: State):
        """Route to appropriate flow based on classified intent."""
        intent = state.get("intent", "rag")
        if intent == "summary":
            return "summary_flow"
        if intent == "interview":
            return "interview_flow"
        if intent == "interview_continue":
            return "interview_continue_flow"
        if intent == "end_interview":
            return "end_interview_flow"
        return "rag_flow"

    # Add conditional routing
    graph.add_conditional_edges("classify", router, {
        "summary_flow": "summary_flow",
        "interview_flow": "interview_flow",
        "interview_continue_flow": "interview_continue_flow",
        "end_interview_flow": "end_interview_flow",
        "rag_flow": "rag_flow"
    })
    
    # All flows end the conversation
    graph.add_edge("summary_flow", END)
    graph.add_edge("interview_flow", END)
    graph.add_edge("interview_continue_flow", END)
    graph.add_edge("end_interview_flow", END)
    graph.add_edge("rag_flow", END)

    return graph.compile()


# Compile the graph once at module load
_GRAPH = _build_graph()


async def run_flow(file_id: str, question: str, conversation_session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Main entry point for conversation orchestration.
    
    Args:
        file_id: ID of the uploaded document
        question: User's question or request
        conversation_session_id: Optional session ID for conversation continuity
        
    Returns:
        Dict containing response with intent, answer, and conversation state
    """
    initial_state: State = {
        "file_id": file_id, 
        "question": question,
        "conversation_session_id": conversation_session_id
    }
    
    # Execute the conversation flow
    result = await _GRAPH.ainvoke(initial_state)
    
    # Build response with essential information
    response = {
        "intent": result.get("intent"), 
        "answer": result.get("answer")
    }
    
    # Include conversation state for interactive flows (interviews)
    if result.get("conversation_session_id"):
        response["conversation_session_id"] = result["conversation_session_id"]
    if result.get("requires_response"):
        response["requires_response"] = result["requires_response"]
    if result.get("conversation_state"):
        response["conversation_state"] = result["conversation_state"]
        
    return response
