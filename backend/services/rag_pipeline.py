import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

from .vectorstore import create_from_texts, get_vectorstore, collection_count
from .embeddings import STEmbeddings
from .llm import get_gemini_llm


def store_embeddings(text, file_id):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.split_text(text)
    if not docs:
        return None
    embeddings = STEmbeddings()
    return create_from_texts(docs, str(file_id), embeddings)


# Async counterparts leveraging threads for blocking CPU/IO tasks
async def astore_embeddings(text: str, file_id: str):
    """Async wrapper for store_embeddings to avoid blocking event loop."""
    return await asyncio.to_thread(store_embeddings, text, file_id)


async def aask_question(file_id: str, query: str) -> str:
    """Async Q&A. If the underlying chain supports arun, use it; otherwise run in a thread."""
    if collection_count(str(file_id)) == 0:
        raise ValueError("No embeddings found for this file. Upload a PDF and ensure embeddings are created before asking questions.")
    
    try:
        vectorstore = get_vectorstore(str(file_id), STEmbeddings())
        retriever = vectorstore.as_retriever()
        llm = get_gemini_llm()
        qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever, chain_type="stuff")
        arun = getattr(qa_chain, "arun", None)
        if callable(arun):
            return await qa_chain.arun(query)
        return await asyncio.to_thread(qa_chain.run, query)
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "limit" in error_msg.lower():
            return "I'm currently experiencing API rate limits. The question you asked was about the uploaded document, but I'm unable to process it right now. Please try again later or contact support for assistance."
        else:
            return f"I encountered an error while processing your question: {error_msg}. Please try rephrasing your question or try again later."

def ask_question(file_id, query):
    if collection_count(str(file_id)) == 0:
        raise ValueError("No embeddings found for this file. Upload a PDF and ensure embeddings are created before asking questions.")
    
    try:
        vectorstore = get_vectorstore(str(file_id), STEmbeddings())
        retriever = vectorstore.as_retriever()
        llm = get_gemini_llm()
        qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever, chain_type="stuff")
        return qa_chain.run(query)
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "limit" in error_msg.lower():
            return "I'm currently experiencing API rate limits. The question you asked was about the uploaded document, but I'm unable to process it right now. Please try again later or contact support for assistance."
        else:
            return f"I encountered an error while processing your question: {error_msg}. Please try rephrasing your question or try again later."
