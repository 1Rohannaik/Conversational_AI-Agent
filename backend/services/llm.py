import os
from langchain_google_genai import ChatGoogleGenerativeAI


def get_google_api_key() -> str:
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY is not set. Add it to backend/.env or your environment.")
    return key


def get_gemini_llm(model: str = "gemini-flash-latest", temperature: float = 0.2) -> ChatGoogleGenerativeAI:
    """Get Gemini LLM with proper configuration."""
    return ChatGoogleGenerativeAI(
        model=model, 
        api_key=get_google_api_key(), 
        temperature=temperature
    )


def get_llm_response(prompt: str, temperature: float = 0.1) -> str:
    """Get a simple LLM response for intent detection and quick queries."""
    try:
        llm = get_gemini_llm(temperature=temperature)
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        raise RuntimeError(f"LLM request failed: {e}")
