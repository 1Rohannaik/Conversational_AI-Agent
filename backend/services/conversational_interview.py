import asyncio
import os
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

from .vectorstore import get_vectorstore, collection_count
from .embeddings import STEmbeddings
from .llm import get_gemini_llm


class ConversationState(Enum):
    WAITING_FOR_FOCUS = "waiting_for_focus"
    ACTIVE_INTERVIEW = "active_interview"
    COMPLETED = "completed"


@dataclass
class ConversationalSession:
    session_id: str
    file_id: str
    state: ConversationState
    focus: Optional[str] = None
    current_question: Optional[str] = None
    question_number: int = 0
    total_questions: int = 5
    context: Optional[str] = None
    last_response: Optional[str] = None


class ConversationalInterviewManager:
    """Manages LLM-driven conversational interview sessions that start with 'take my interview'."""
    
    def __init__(self) -> None:
        self._sessions: Dict[str, ConversationalSession] = {}

    def create_session(self, file_id: str) -> ConversationalSession:
        """Create a new conversational interview session."""
        session_id = str(uuid.uuid4())
        session = ConversationalSession(
            session_id=session_id,
            file_id=file_id,
            state=ConversationState.WAITING_FOR_FOCUS
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[ConversationalSession]:
        """Get an existing session."""
        return self._sessions.get(session_id)

    def update_session(self, session_id: str, **kwargs) -> None:
        """Update session properties."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)

    def end_session(self, session_id: str) -> None:
        """End and cleanup session."""
        if session_id in self._sessions:
            del self._sessions[session_id]

    async def get_pdf_context(self, file_id: str, focus: str) -> str:
        """Get relevant context from PDF based on focus area."""
        try:
            if collection_count(str(file_id)) == 0:
                raise ValueError("No embeddings found for this file. Upload and embed first.")
            
            vectorstore = get_vectorstore(str(file_id), STEmbeddings())
            retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
            
            # Get relevant documents based on focus
            docs = await asyncio.to_thread(retriever.get_relevant_documents, focus)
            context = "\n\n".join([d.page_content for d in docs if getattr(d, "page_content", None)])
            
            return context
        except Exception as e:
            print(f"Error getting PDF context: {e}")
            return ""

    async def generate_first_question(self, file_id: str, focus: str) -> str:
        """Generate the first interview question using LLM based on focus and PDF content."""
        context = await self.get_pdf_context(file_id, focus)
        
        llm = get_gemini_llm(temperature=0.3)
        prompt = f"""You are an expert interviewer conducting a technical interview focused on {focus}.

Based on the provided PDF content, generate ONE well-crafted interview question that:
1. Tests fundamental understanding of {focus}
2. Is relevant to the content in the PDF
3. Is appropriate for an intermediate level candidate
4. Requires a thoughtful answer (not just yes/no)

PDF Content:
{context[:3000] if context else "No specific content available"}

Generate only the question, no additional text or formatting:"""

        try:
            response = await asyncio.to_thread(llm.invoke, prompt)
            question = getattr(response, "content", str(response)).strip()
            return question
        except Exception as e:
            print(f"Error generating question: {e}")
            return f"Can you explain the key concepts in {focus} based on the document you uploaded?"

    async def evaluate_answer_and_generate_next(self, session: ConversationalSession, user_answer: str) -> Dict:
        """Evaluate user's answer and generate next question or feedback."""
        context = session.context or ""
        current_question = session.current_question
        focus = session.focus
        question_num = session.question_number
        total_questions = session.total_questions
        
        llm = get_gemini_llm(temperature=0.2)
        
        # If this is the last question, provide final evaluation
        if question_num >= total_questions:
            prompt = f"""You are an expert interviewer evaluating the final answer in a {focus} interview.

Question asked: {current_question}
User's answer: {user_answer}

Provide a comprehensive evaluation that includes:
1. Whether the answer is correct/partially correct/incorrect
2. Key points they got right
3. What they missed (if anything)
4. Overall interview performance summary
5. Encouragement and suggestions for improvement

Keep the tone professional but encouraging. This is the end of the interview."""

            try:
                response = await asyncio.to_thread(llm.invoke, prompt)
                feedback = getattr(response, "content", str(response)).strip()
                
                return {
                    "feedback": feedback,
                    "is_correct": True,  # We don't fail anyone at the end
                    "next_question": None,
                    "completed": True
                }
            except Exception as e:
                return {
                    "feedback": "Thank you for completing the interview! You showed good understanding of the topics.",
                    "is_correct": True,
                    "next_question": None,
                    "completed": True
                }
        
        # Evaluate current answer and generate next question
        prompt = f"""You are an expert interviewer conducting a {focus} interview.

Previous question: {current_question}
User's answer: {user_answer}
PDF Context: {context[:2000] if context else "No specific content"}

Your task:
1. Evaluate if the answer is correct, partially correct, or incorrect
2. Provide brief feedback (2-3 sentences max)
3. Generate the next interview question that:
   - Builds on previous topics or explores new areas
   - Tests different aspects of {focus}
   - Is appropriate for intermediate level
   - Is relevant to the PDF content when possible

Respond in this exact format:
EVALUATION: [correct/partial/incorrect]
FEEDBACK: [Your brief feedback here]
NEXT_QUESTION: [Your next interview question here]"""

        try:
            response = await asyncio.to_thread(llm.invoke, prompt)
            content = getattr(response, "content", str(response)).strip()
            
            # Parse the response
            lines = content.split('\n')
            evaluation = "partial"  # default
            feedback = "Thank you for your answer."
            next_question = f"Can you tell me more about another aspect of {focus}?"
            
            for line in lines:
                if line.startswith("EVALUATION:"):
                    eval_text = line.replace("EVALUATION:", "").strip().lower()
                    if "correct" in eval_text and "incorrect" not in eval_text:
                        evaluation = "correct"
                    elif "incorrect" in eval_text:
                        evaluation = "incorrect"
                    else:
                        evaluation = "partial"
                elif line.startswith("FEEDBACK:"):
                    feedback = line.replace("FEEDBACK:", "").strip()
                elif line.startswith("NEXT_QUESTION:"):
                    next_question = line.replace("NEXT_QUESTION:", "").strip()
            
            is_correct = evaluation in ["correct", "partial"]
            
            return {
                "feedback": feedback,
                "is_correct": is_correct,
                "next_question": next_question,
                "completed": False
            }
            
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return {
                "feedback": "Thank you for your answer. Let's continue with the next question.",
                "is_correct": True,
                "next_question": f"Can you explain another important concept related to {focus}?",
                "completed": False
            }


# Global manager instance
conversation_manager = ConversationalInterviewManager()


async def handle_conversational_interview(file_id: str, user_input: str, session_id: Optional[str] = None) -> Dict:
    """
    Handle the LLM-driven conversational interview flow:
    1. Start -> ask for focus
    2. Get focus -> generate first question using LLM
    3. Continue -> evaluate answers and generate next questions using LLM
    """
    
    # Check if we have an existing session
    session = None
    if session_id:
        session = conversation_manager.get_session(session_id)
    
    # If no session, this is the initial "take my interview" request
    if not session:
        session = conversation_manager.create_session(file_id)
        return {
            "session_id": session.session_id,
            "response": "What would you like to focus on for this interview? For example, you could say 'backend development', 'machine learning', 'data structures', 'system design', or any specific topic from your PDF.",
            "state": "waiting_for_focus",
            "requires_response": True
        }
    
    # Handle based on current state
    if session.state == ConversationState.WAITING_FOR_FOCUS:
        # User provided focus, start the LLM-driven interview
        focus = user_input.strip()
        
        try:
            # Get PDF context and generate first question
            context = await conversation_manager.get_pdf_context(file_id, focus)
            first_question = await conversation_manager.generate_first_question(file_id, focus)
            
            # Update session
            conversation_manager.update_session(
                session.session_id,
                state=ConversationState.ACTIVE_INTERVIEW,
                focus=focus,
                context=context,
                current_question=first_question,
                question_number=1
            )
            
            return {
                "session_id": session.session_id,
                "response": f"Great! I'll interview you on {focus}. Let's begin:\n\n{first_question}",
                "state": "active_interview",
                "progress": f"Question 1 of {session.total_questions}",
                "requires_response": True
            }
            
        except ValueError as e:
            return {
                "session_id": session.session_id,
                "response": f"Sorry, I couldn't start the interview: {str(e)}. Please make sure you have uploaded and processed a PDF first.",
                "state": "error",
                "requires_response": False
            }
    
    elif session.state == ConversationState.ACTIVE_INTERVIEW:
        # User provided an answer, evaluate it and generate next question
        try:
            result = await conversation_manager.evaluate_answer_and_generate_next(session, user_input)
            
            if result["completed"]:
                # Interview completed
                conversation_manager.update_session(
                    session.session_id,
                    state=ConversationState.COMPLETED
                )
                
                return {
                    "session_id": session.session_id,
                    "response": f"{result['feedback']}\n\nCongratulations! Your interview is now complete. Would you like to start another interview or ask me something else?",
                    "state": "completed",
                    "progress": f"Interview completed ({session.total_questions}/{session.total_questions})",
                    "requires_response": False
                }
            else:
                # Continue with next question
                next_question_num = session.question_number + 1
                
                conversation_manager.update_session(
                    session.session_id,
                    current_question=result["next_question"],
                    question_number=next_question_num
                )
                
                response_parts = [result["feedback"]]
                if result["next_question"]:
                    response_parts.append(f"\nNext question:\n{result['next_question']}")
                
                return {
                    "session_id": session.session_id,
                    "response": "\n\n".join(response_parts),
                    "state": "active_interview",
                    "progress": f"Question {next_question_num} of {session.total_questions}",
                    "requires_response": True
                }
                
        except Exception as e:
            print(f"Error in interview flow: {e}")
            return {
                "session_id": session.session_id,
                "response": f"I encountered an error processing your answer. Let me ask you another question about {session.focus}.",
                "state": "active_interview",
                "requires_response": True
            }
    
    else:
        # Session completed or in error state
        conversation_manager.end_session(session.session_id)
        return {
            "response": "Your previous interview session has ended. Say 'take my interview' to start a new one!",
            "state": "new",
            "requires_response": False
        }


def get_conversation_status(session_id: str) -> Optional[Dict]:
    """Get the status of a conversational interview session."""
    session = conversation_manager.get_session(session_id)
    if not session:
        return None
        
    result = {
        "session_id": session.session_id,
        "file_id": session.file_id,
        "state": session.state.value,
        "focus": session.focus,
        "question_number": session.question_number,
        "total_questions": session.total_questions,
        "current_question": session.current_question
    }
            
    return result