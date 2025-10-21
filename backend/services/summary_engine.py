"""
Summary Engine Service

Handles document summarization using RAG-based content retrieval
and LLM-powered summary generation.
"""

import asyncio
from typing import Dict, Any
from .document_analyzer import get_retriever
from .llm import get_gemini_llm


class SummaryEngine:
    """Manages document summarization with comprehensive content analysis."""
    
    @staticmethod
    async def generate_summary(file_id: str, question: str) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the document content.
        
        Uses RAG to retrieve relevant content and LLM to create structured summary.
        """
        try:
            retriever = await get_retriever(file_id)
            docs = await asyncio.to_thread(
                retriever.get_relevant_documents, 
                question or "summary of the document"
            )
            context = "\n\n".join([
                d.page_content for d in docs 
                if getattr(d, "page_content", None)
            ])

            llm = get_gemini_llm()
            prompt = (
                "Please provide a comprehensive summary of the document content below.\n"
                "Include the main topics, key concepts, and important details.\n"
                "Structure your response with clear headings and bullet points.\n\n"
                f"Document content:\n{context}\n\n"
                f"Focus area (if specified): {question}"
            )
            
            resp = await asyncio.to_thread(llm.invoke, prompt)
            
            return {
                "answer": getattr(resp, "content", str(resp)),
                "intent": "summary"
            }
            
        except Exception as e:
            return SummaryEngine._get_fallback_response(str(e))
    
    @staticmethod
    def _get_fallback_response(error_msg: str) -> Dict[str, Any]:
        """Fallback response for summary generation failures."""
        if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            answer = (
                "I'm currently experiencing high usage and have reached my API limits. "
                "Please try again in a few minutes, or use specific questions about your "
                "document instead of requesting a summary."
            )
        else:
            answer = f"Sorry, I encountered an error while generating the summary: {error_msg}"
        
        return {
            "answer": answer,
            "intent": "summary"
        }