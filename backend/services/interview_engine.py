"""
Interview Engine Service

Handles the hybrid RAG + generative reasoning for conducting AI-driven interviews.
Combines document analysis with dynamic question generation.
"""

import asyncio
import uuid
import random
from typing import Dict, Any
from .document_analyzer import analyze_document_for_interview, get_document_context
from .llm import get_gemini_llm


class InterviewEngine:
    """Manages AI-driven interview sessions with hybrid RAG + generative approach."""
    
    @staticmethod
    async def start_interview(file_id: str, question: str) -> Dict[str, Any]:
        """
        Start a new interview session using hybrid RAG + generative approach.
        
        Phase 1: Document Analysis (RAG) - Extract key insights
        Phase 2: Generative Reasoning - Create contextual interview question
        """
        try:
            # PHASE 1: Document Analysis (RAG)
            document_analysis = await analyze_document_for_interview(file_id)
            
            # PHASE 2: Generative Reasoning - Create contextual interview question
            llm = get_gemini_llm()
            
            interview_prompt = (
                "You are conducting a professional interview. Based on the document analysis below, "
                "generate ONE thoughtful, relevant interview question that:\n"
                "1. Tests knowledge/skills mentioned in the document\n"
                "2. Is appropriate for the candidate's experience level\n"
                "3. Encourages detailed explanation and reasoning\n"
                "4. Is engaging and realistic for a job interview\n\n"
                f"Document Analysis:\n{document_analysis}\n\n"
                f"User request context: {question}\n\n"
                "Create a single, clear interview question that balances the candidate's background "
                "with challenging but fair assessment. Do NOT provide the answer. "
                "End with 'Please share your thoughts and reasoning.'"
            )
            
            resp = await asyncio.to_thread(llm.invoke, interview_prompt)
            interview_response = getattr(resp, "content", str(resp))
            
            # Generate session ID
            session_id = str(uuid.uuid4())[:8]
            
            # Add professional opening
            opening = (
                f"Perfect! I've analyzed your document and I'm ready to conduct your interview. "
                f"Let me start with a question tailored to your background.\n\n{interview_response}"
            )
            
            return {
                "answer": opening,
                "intent": "interview",
                "conversation_session_id": session_id,
                "requires_response": True,
                "conversation_state": "active_interview",
                "document_analysis": document_analysis
            }
            
        except Exception as e:
            return InterviewEngine._get_fallback_start_response(str(e))
    
    @staticmethod
    async def continue_interview(file_id: str, user_answer: str, document_analysis: str = "") -> Dict[str, Any]:
        """
        Continue interview with feedback and next question.
        
        Uses hybrid approach: evaluate answer + generate contextual follow-up.
        """
        try:
            # Get document analysis if not provided
            if not document_analysis:
                document_analysis = await analyze_document_for_interview(file_id)
            
            llm = get_gemini_llm()
            
            # HYBRID APPROACH: Evaluate answer + Generate next question
            continue_prompt = (
                "You are continuing a job interview. Analyze the candidate's answer and ask a follow-up question.\n\n"
                "INSTRUCTIONS:\n"
                "1. Give brief feedback on their answer (2-3 sentences)\n"
                "2. Generate ONE new interview question based on the document analysis\n"
                "3. Make the question challenging but fair for their experience level\n"
                "4. Focus on different aspect than the previous question\n"
                "5. Do NOT provide answers, only ask questions\n\n"
                f"Document Analysis (candidate's background):\n{document_analysis}\n\n"
                f"Candidate's answer to evaluate:\n{user_answer}\n\n"
                "Provide constructive feedback on their answer, then ask a new interview question "
                "that tests a different skill/area from their background. "
                "End with 'Please share your thoughts and reasoning.'"
            )
            
            resp = await asyncio.to_thread(llm.invoke, continue_prompt)
            
            return {
                "answer": getattr(resp, "content", str(resp)),
                "intent": "interview_continue",
                "requires_response": True,
                "conversation_state": "active_interview",
                "document_analysis": document_analysis
            }
            
        except Exception as e:
            return InterviewEngine._get_fallback_continue_response(str(e))
    
    @staticmethod
    async def end_interview(file_id: str) -> Dict[str, Any]:
        """Provide professional interview conclusion with personalized feedback."""
        try:
            # Get context for personalized feedback
            context = await get_document_context(file_id, "skills experience background")
            limited_context = "\n\n".join(context.split("\n\n")[:2])  # Limit for brevity
            
            llm = get_gemini_llm()
            
            conclusion_prompt = (
                "Provide a professional interview conclusion. Based on the candidate's background, "
                "give encouraging feedback and next steps advice.\n\n"
                "Keep it concise (3-4 sentences) and include:\n"
                "1. Thank them for their time\n"
                "2. Brief positive comment about their background\n"
                "3. General advice or encouragement\n\n"
                f"Candidate background:\n{limited_context}\n\n"
                "Be professional, encouraging, and authentic."
            )
            
            resp = await asyncio.to_thread(llm.invoke, conclusion_prompt)
            conclusion = getattr(resp, "content", str(resp))
            
            return {
                "answer": f"🎯 **Interview Complete!**\n\n{conclusion}\n\nFeel free to ask me any specific questions about your document or request another interview anytime!",
                "intent": "end_interview",
                "conversation_session_id": None,
                "requires_response": False,
                "conversation_state": "completed"
            }
            
        except Exception:
            return InterviewEngine._get_fallback_end_response()
    
    @staticmethod
    def _get_fallback_start_response(error_msg: str) -> Dict[str, Any]:
        """Fallback response for interview start failures."""
        if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            fallback_questions = [
                "Based on your background, can you walk me through your most challenging project and how you approached solving the key problems? Please share your thoughts and reasoning.",
                "Tell me about a time when you had to learn a new technology or skill quickly. What was your approach and what did you learn from the experience? Please share your thoughts and reasoning.",
                "Describe a situation where you had to work with a team to deliver a complex solution. What was your role and how did you ensure success? Please share your thoughts and reasoning.",
                "Can you explain a technical concept from your field that you're passionate about, and how you've applied it in practice? Please share your thoughts and reasoning."
            ]
            selected_question = random.choice(fallback_questions)
            answer = f"I'd be happy to conduct your interview! I'm currently experiencing high API usage, but let me ask you this relevant question:\n\n{selected_question}"
        else:
            answer = f"I'd like to conduct your interview, but encountered an error: {error_msg}. Let's start with a basic question: Can you tell me about your most significant accomplishment mentioned in your document? Please share your thoughts and reasoning."
        
        return {
            "answer": answer,
            "intent": "interview",
            "conversation_session_id": str(uuid.uuid4())[:8],
            "requires_response": True,
            "conversation_state": "active_interview"
        }
    
    @staticmethod
    def _get_fallback_continue_response(error_msg: str) -> Dict[str, Any]:
        """Fallback response for interview continuation failures."""
        if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            feedback_options = [
                "Thank you for your detailed response. That shows good analytical thinking.",
                "I appreciate your explanation. You've demonstrated clear understanding of the concepts.",
                "Good answer! Your approach shows practical experience and problem-solving skills.",
                "Excellent! Your response indicates strong technical knowledge and experience."
            ]
            
            followup_questions = [
                "Now, let's shift focus - can you describe a time when you had to debug a particularly challenging issue? What was your systematic approach? Please share your thoughts and reasoning.",
                "Moving to a different area - how do you stay updated with new technologies and trends in your field? Can you give me a specific example? Please share your thoughts and reasoning.",
                "Let's explore collaboration - tell me about a time you had to explain a complex technical concept to non-technical stakeholders. How did you approach it? Please share your thoughts and reasoning.",
                "Switching topics - describe a situation where you had to make a critical technical decision under pressure. What factors did you consider? Please share your thoughts and reasoning."
            ]
            
            feedback = random.choice(feedback_options)
            next_question = random.choice(followup_questions)
            answer = f"{feedback}\n\n{next_question}"
        else:
            answer = f"Thank you for your answer. I encountered an error: {error_msg}. Let's continue - can you tell me about how you approach learning new technologies or solving complex problems? Please share your thoughts and reasoning."
        
        return {
            "answer": answer,
            "intent": "interview_continue",
            "requires_response": True,
            "conversation_state": "active_interview"
        }
    
    @staticmethod
    def _get_fallback_end_response() -> Dict[str, Any]:
        """Fallback response for interview end failures."""
        return {
            "answer": (
                "🎯 **Interview Complete!**\n\n"
                "Thank you for participating in this interview session! Based on our conversation, "
                "you've demonstrated good analytical thinking and communication skills. "
                "Keep building on your strengths and continue learning.\n\n"
                "Feel free to ask me any specific questions about your document or request another interview anytime!"
            ),
            "intent": "end_interview",
            "conversation_session_id": None,
            "requires_response": False,
            "conversation_state": "completed"
        }