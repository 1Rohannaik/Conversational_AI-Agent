import os
from groq import Groq
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file

def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        # Defer error until the function is called, not at import time
        raise RuntimeError(
            "Missing GROQ_API_KEY environment variable. Set it before calling the STT endpoint."
        )
    return Groq(api_key=api_key)

def transcribe_audio_with_groq(audio_file_path: str, model: str = "whisper-large-v3"):
    """
    Transcribe audio file using Groq STT API.
    Args:
        audio_file_path: path to WAV/MP3 file
        model: Groq model to use
    Returns:
        transcription text
    """
    client = _get_client()
    with open(audio_file_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model=model,
            file=f,
            language="en"
        )
    return transcription.text
