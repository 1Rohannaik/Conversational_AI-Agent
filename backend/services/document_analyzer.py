"""
Document Analysis Service

Handles RAG-based document analysis for extracting key information
like skills, experience, projects, and education from uploaded documents.
"""

import asyncio
import os
from typing import Dict, Any
from .vectorstore import get_vectorstore, collection_count
from .embeddings import STEmbeddings
from .llm import get_gemini_llm


async def get_retriever(file_id: str):
    """Get a retriever for the specified file."""
    if collection_count(str(file_id)) == 0:
        raise ValueError("No embeddings found for this file. Upload and embed first.")
    vectorstore = get_vectorstore(str(file_id), STEmbeddings())
    retriever = vectorstore.as_retriever(search_kwargs={"k": int(os.getenv("RAG_TOP_K", "6"))})
    return retriever


async def analyze_document_for_interview(file_id: str) -> str:
    """
    Analyze document content to extract key information for interview context.
    
    Returns structured analysis of skills, experience, projects, and education.
    """
    try:
        retriever = await get_retriever(file_id)
        
        # Get content for analysis
        analysis_docs = await asyncio.to_thread(
            retriever.get_relevant_documents, 
            "skills experience education projects technologies background"
        )
        document_content = "\n\n".join([
            d.page_content for d in analysis_docs 
            if getattr(d, "page_content", None)
        ])

        llm = get_gemini_llm()
        
        # Analyze the document to extract key interview-relevant information
        analysis_prompt = (
            "Analyze this document and extract key information for conducting a relevant interview.\n"
            "Focus on: skills, experience level, technologies mentioned, projects, education, and expertise areas.\n"
            "Provide a concise analysis in this format:\n"
            "KEY SKILLS: [list main technical/professional skills]\n"
            "EXPERIENCE LEVEL: [junior/mid/senior based on content]\n"
            "MAIN AREAS: [key domains/technologies/subjects]\n"
            "NOTABLE PROJECTS: [significant work/achievements mentioned]\n\n"
            f"Document content:\n{document_content}"
        )
        
        analysis_resp = await asyncio.to_thread(llm.invoke, analysis_prompt)
        return getattr(analysis_resp, "content", str(analysis_resp))
        
    except Exception as e:
        # Return basic fallback analysis
        return (
            "KEY SKILLS: General technical and professional skills\n"
            "EXPERIENCE LEVEL: To be determined through interview\n"
            "MAIN AREAS: Based on uploaded document content\n"
            "NOTABLE PROJECTS: Professional experience and achievements"
        )


async def get_document_context(file_id: str, query: str) -> str:
    """Get relevant document context for a specific query."""
    try:
        retriever = await get_retriever(file_id)
        docs = await asyncio.to_thread(retriever.get_relevant_documents, query)
        return "\n\n".join([
            d.page_content for d in docs 
            if getattr(d, "page_content", None)
        ])
    except Exception:
        return ""