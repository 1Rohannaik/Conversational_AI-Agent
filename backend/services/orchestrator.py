import os
import asyncio
from typing import Dict, Any, Optional

from langgraph.graph import StateGraph, END

from .vectorstore import get_vectorstore, collection_count
from .embeddings import STEmbeddings
from .llm import get_gemini_llm, get_google_api_key
from .rag_pipeline import aask_question
from .conversational_interview import handle_conversational_interview


# Simple state container for LangGraph
State = Dict[str, Any]


async def _get_retriever(file_id: str):
    if collection_count(str(file_id)) == 0:
        raise ValueError("No embeddings found for this file. Upload and embed first.")
    vectorstore = get_vectorstore(str(file_id), STEmbeddings())
    retriever = vectorstore.as_retriever(search_kwargs={"k": int(os.getenv("RAG_TOP_K", "6"))})
    return retriever


async def _classify_intent(question: str, conversation_session_id: Optional[str] = None) -> str:
    """LLM-based lightweight intent classification: quiz | summary | interview | interview_start | conversation_continue | rag."""
    
    # If we have a conversation session ID, this is likely a continuation
    if conversation_session_id:
        from .conversational_interview import conversation_manager, ConversationState
        session = conversation_manager.get_session(conversation_session_id)
        if session and session.state == ConversationState.ACTIVE_INTERVIEW:
            return "interview_start"  # Continue using the same flow
    
    llm = get_gemini_llm(model="gemini-flash-latest", temperature=0.0)
    prompt = (
        "Classify the user's intent as one of: quiz, summary, interview_start, interview, rag.\n"
        "- If the user asks to generate quiz/questions/MCQs, return 'quiz'.\n"
        "- If the user asks to summarize/synopsis/overview, return 'summary'.\n"
        "- If the user says 'take my interview' or 'start interview' or 'interview me', return 'interview_start'.\n"
        "- If the user asks to prepare interview questions, behavioral/technical interview prep, or mock interview, return 'interview'.\n"
        "- Otherwise, return 'rag'.\n"
        f"User: {question}\n"
        "Reply with only one word: quiz, summary, interview_start, interview, or rag."
    )
    
    # Offload to thread as a safe default
    resp = await asyncio.to_thread(llm.invoke, prompt)
    raw = getattr(resp, "content", str(resp))
    raw = (raw or "").strip().lower()
    if "quiz" in raw:
        return "quiz"
    if "summary" in raw:
        return "summary"
    if "interview_start" in raw:
        return "interview_start"
    if "interview" in raw or "mock interview" in raw:
        return "interview"
    return "rag"
async def _run_quiz_flow(state: State) -> State:
    file_id = str(state["file_id"])  # required
    question = state["question"]
    retriever = await _get_retriever(file_id)
    # Broad retrieval; use the question to bias topics if provided
    docs = await asyncio.to_thread(retriever.get_relevant_documents, question or "")
    context = "\n\n".join([d.page_content for d in docs if getattr(d, "page_content", None)])

    llm = get_gemini_llm()
    prompt = (
        "You are an educational assistant. Based on the provided context, create practice questions.\n"
        "Generate 5 questions maximum. Mix multiple choice and short answer formats.\n"
        "Provide clear, concise answers for each question.\n\n"
        f"Context:\n{context}\n\n"
        f"User request: {question}\n\n"
        "Format your response as a numbered list with questions and answers."
    )
    resp = await asyncio.to_thread(llm.invoke, prompt)
    state["answer"] = getattr(resp, "content", str(resp))
    state["intent"] = "quiz"
    return state


async def _run_summary_flow(state: State) -> State:
    file_id = str(state["file_id"])  # required
    question = state["question"]
    retriever = await _get_retriever(file_id)
    docs = await asyncio.to_thread(retriever.get_relevant_documents, question or "summary of the document")
    context = "\n\n".join([d.page_content for d in docs if getattr(d, "page_content", None)])

    llm = get_gemini_llm()
    prompt = (
        "Please provide a comprehensive summary of the document content below.\n"
        "Include the main topics, key concepts, and important details.\n"
        "Structure your response with clear headings and bullet points.\n\n"
        f"Document content:\n{context}\n\n"
        f"Focus area (if specified): {question}"
    )
    resp = await asyncio.to_thread(llm.invoke, prompt)
    state["answer"] = getattr(resp, "content", str(resp))
    state["intent"] = "summary"
    return state


async def _run_interview_start_flow(state: State) -> State:
    """Handle 'take my interview' requests using conversational interview service."""
    file_id = str(state["file_id"])
    question = state["question"]
    
    # Use the conversational interview service
    result = await handle_conversational_interview(
        file_id=file_id,
        user_input=question,
        session_id=state.get("conversation_session_id")
    )
    
    state["answer"] = result["response"]
    state["intent"] = "interview_start"
    state["conversation_session_id"] = result.get("session_id")
    state["conversation_state"] = result.get("state")
    state["requires_response"] = result.get("requires_response", False)
    
    # Store additional context
    if "interview_session_id" in result:
        state["interview_session_id"] = result["interview_session_id"]
    if "progress" in result:
        state["progress"] = result["progress"]
    
    return state


async def _run_rag_flow(state: State) -> State:
    file_id = str(state["file_id"])  # required
    question = state["question"]
    answer = await aask_question(file_id, question)
    state["answer"] = answer
    state["intent"] = "rag"
    return state


async def _run_interview_flow(state: State) -> State:
    file_id = str(state["file_id"])  # required
    question = state["question"]
    retriever = await _get_retriever(file_id)
    # Focus retrieval using the user's topic if present
    docs = await asyncio.to_thread(retriever.get_relevant_documents, question or "interview preparation")
    context = "\n\n".join([d.page_content for d in docs if getattr(d, "page_content", None)])

    llm = get_gemini_llm()
    prompt = (
        "You are a career coach helping with job preparation. Based on the content provided, create:\n"
        "1. 3-5 technical questions related to the material\n"
        "2. 2-3 behavioral questions\n"
        "3. Sample answers or key points to address\n"
        "4. Tips for presenting your knowledge effectively\n\n"
        f"Reference material:\n{context}\n\n"
        f"Specific focus area: {question}\n\n"
        "Structure your response clearly with numbered sections."
    )
    resp = await asyncio.to_thread(llm.invoke, prompt)
    state["answer"] = getattr(resp, "content", str(resp))
    state["intent"] = "interview"
    return state


def _build_graph():
    graph = StateGraph(dict)

    async def classify_node(state: State) -> State:
        intent = state.get("intent") or await _classify_intent(
            state["question"], 
            state.get("conversation_session_id")
        )
        state["intent"] = intent
        return state

    graph.add_node("classify", classify_node)
    graph.add_node("quiz_flow", _run_quiz_flow)
    graph.add_node("summary_flow", _run_summary_flow)
    graph.add_node("interview_start_flow", _run_interview_start_flow)
    graph.add_node("rag_flow", _run_rag_flow)
    graph.add_node("interview_flow", _run_interview_flow)

    graph.set_entry_point("classify")

    def router(state: State):
        intent = state.get("intent", "rag")
        if intent == "quiz":
            return "quiz_flow"
        if intent == "summary":
            return "summary_flow"
        if intent == "interview_start":
            return "interview_start_flow"
        if intent == "interview":
            return "interview_flow"
        return "rag_flow"

    graph.add_conditional_edges("classify", router, {
        "quiz_flow": "quiz_flow", 
        "summary_flow": "summary_flow", 
        "interview_start_flow": "interview_start_flow",
        "interview_flow": "interview_flow", 
        "rag_flow": "rag_flow"
    })
    graph.add_edge("quiz_flow", END)
    graph.add_edge("summary_flow", END)
    graph.add_edge("interview_start_flow", END)
    graph.add_edge("rag_flow", END)
    graph.add_edge("interview_flow", END)

    return graph.compile()


_GRAPH = _build_graph()


async def run_flow(file_id: str, question: str, conversation_session_id: Optional[str] = None) -> Dict[str, Any]:
    initial: State = {
        "file_id": file_id, 
        "question": question,
        "conversation_session_id": conversation_session_id
    }
    result = await _GRAPH.ainvoke(initial)
    
    # Return additional conversation context if available
    response = {"intent": result.get("intent"), "answer": result.get("answer")}
    
    if result.get("conversation_session_id"):
        response["conversation_session_id"] = result["conversation_session_id"]
    if result.get("conversation_state"):
        response["conversation_state"] = result["conversation_state"]
    if result.get("requires_response"):
        response["requires_response"] = result["requires_response"]
    if result.get("progress"):
        response["progress"] = result["progress"]
        
    return response
