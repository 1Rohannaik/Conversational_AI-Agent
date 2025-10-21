import asyncio
import os
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

from .vectorstore import get_vectorstore, collection_count
from .embeddings import STEmbeddings
from .llm import get_gemini_llm


@dataclass
class InterviewSession:
    session_id: str
    file_id: str
    total_questions: int
    asked: int = 0
    history: List[Tuple[str, str]] = field(default_factory=list)  # (role, content)
    last_question: Optional[str] = None
    done: bool = False
    focus: Optional[str] = None
    level: Optional[str] = None


class InterviewSessionManager:
    """In-memory session manager for interactive interviews.

    NOTE: Sessions are not persisted and will be lost on server restart.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, InterviewSession] = {}

    def create(self, file_id: str, total_questions: int, focus: Optional[str], level: Optional[str]) -> InterviewSession:
        sid = str(uuid.uuid4())
        session = InterviewSession(
            session_id=sid,
            file_id=file_id,
            total_questions=max(1, min(total_questions, 10)),
            focus=(focus or None),
            level=(level or None),
        )
        self._sessions[sid] = session
        return session

    def get(self, session_id: str) -> InterviewSession:
        s = self._sessions.get(session_id)
        if not s:
            raise KeyError("Invalid or expired session_id")
        return s

    def end(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]


manager = InterviewSessionManager()


async def _get_retrieved_context(file_id: str, topic_hint: str = "") -> str:
    if collection_count(str(file_id)) == 0:
        raise ValueError("No embeddings found for this file. Upload and embed first.")
    retriever = get_vectorstore(str(file_id), STEmbeddings()).as_retriever(
        search_kwargs={"k": int(os.getenv("RAG_TOP_K", "6"))}
    )
    docs = await asyncio.to_thread(retriever.get_relevant_documents, topic_hint or "technical interview")
    return "\n\n".join([d.page_content for d in docs if getattr(d, "page_content", None)])


async def _generate_first_question(session: InterviewSession) -> str:
    context = await _get_retrieved_context(session.file_id, session.focus or "")
    llm = get_gemini_llm()
    prompt = (
        "You are a strict yet supportive technical interviewer.\n"
        "Ask exactly ONE concise question at a time. Do not include answers or hints.\n"
        "Tailor the question to the candidate's level and the provided context.\n"
        "Keep it grounded in the context and avoid trivialities.\n\n"
        f"Candidate level: {session.level or 'unspecified'}\n"
        f"Focus/topic: {session.focus or 'general'}\n\n"
        "Context from the candidate's materials:\n"
        f"{context}\n\n"
        "Now ask the FIRST question only."
    )
    resp = await asyncio.to_thread(llm.invoke, prompt)
    return getattr(resp, "content", str(resp)).strip()


async def _evaluate_and_next(session: InterviewSession, answer: str) -> Tuple[str, Optional[str], bool]:
    """Return (feedback, next_question_or_none, done)."""
    context = await _get_retrieved_context(session.file_id, session.focus or "")
    llm = get_gemini_llm()

    history_snippets = []
    # Include up to last 6 turns for brevity
    for role, content in session.history[-6:]:
        history_snippets.append(f"{role.upper()}: {content}")
    history_text = "\n".join(history_snippets)

    prompt = (
        "You are a technical interviewer. Evaluate the candidate's answer and decide the next step.\n"
        "Rules:\n"
        "- Provide brief, pointed feedback: strengths, gaps, and one improvement tip (3-6 lines).\n"
        "- Then either produce a single, next follow-up question OR say NONE if the interview is complete.\n"
        "- Keep questions grounded in the provided context.\n\n"
        f"Candidate level: {session.level or 'unspecified'}\n"
        f"Focus/topic: {session.focus or 'general'}\n"
        f"Questions asked so far: {session.asked} / {session.total_questions}\n\n"
        "Context from the candidate's materials:\n"
        f"{context}\n\n"
        "Conversation so far (recent):\n"
        f"{history_text}\n\n"
        f"LAST_QUESTION: {session.last_question or 'N/A'}\n"
        f"CANDIDATE_ANSWER: {answer}\n\n"
        "Respond strictly in this format:\n"
        "FEEDBACK: <short feedback>\n"
        "NEXT_QUESTION: <one question or NONE>\n"
    )

    resp = await asyncio.to_thread(llm.invoke, prompt)
    raw = getattr(resp, "content", str(resp)) or ""

    # Parse feedback and next question
    feedback = ""
    next_q: Optional[str] = None
    for line in raw.splitlines():
        if line.strip().lower().startswith("feedback:"):
            feedback = line.split(":", 1)[1].strip()
        elif line.strip().lower().startswith("next_question:"):
            candidate = line.split(":", 1)[1].strip()
            if candidate and candidate.upper() != "NONE":
                next_q = candidate
            else:
                next_q = None

    # Decide completion based on count
    done = session.asked >= session.total_questions
    if done:
        next_q = None

    return feedback or raw.strip(), next_q, done


async def start_interview(file_id: str, num_questions: int = 5, focus: Optional[str] = None, level: Optional[str] = None):
    if collection_count(str(file_id)) == 0:
        raise ValueError("No embeddings found for this file. Upload and embed first.")
    session = manager.create(str(file_id), num_questions, focus, level)
    first_q = await _generate_first_question(session)
    session.last_question = first_q
    session.history.append(("interviewer", first_q))
    session.asked = 1
    return {
        "session_id": session.session_id,
        "question": first_q,
        "progress": {"asked": session.asked, "total": session.total_questions},
    }


async def submit_answer(session_id: str, answer: str):
    session = manager.get(session_id)
    if session.done:
        return {"done": True, "message": "Interview already completed."}

    session.history.append(("candidate", answer))
    feedback, next_q, done = await _evaluate_and_next(session, answer)

    if done or not next_q:
        session.done = True
        return {
            "done": True,
            "feedback": feedback,
            "progress": {"asked": session.asked, "total": session.total_questions},
        }

    # Continue interview
    session.history.append(("interviewer", next_q))
    session.last_question = next_q
    session.asked += 1
    return {
        "done": False,
        "feedback": feedback,
        "question": next_q,
        "progress": {"asked": session.asked, "total": session.total_questions},
    }


def get_status(session_id: str):
    session = manager.get(session_id)
    return {
        "session_id": session.session_id,
        "file_id": session.file_id,
        "done": session.done,
        "last_question": session.last_question,
        "progress": {"asked": session.asked, "total": session.total_questions},
        "focus": session.focus,
        "level": session.level,
    }
