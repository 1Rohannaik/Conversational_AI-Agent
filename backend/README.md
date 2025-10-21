# Gemini Voice RAG Backend

Hybrid Retrieval-Augmented Generation (RAG) + Generative Reasoning backend that powers a voice-first assistant. It understands uploaded PDFs (RAG), conducts dynamic AI interviews tailored to the document, answers factual questions, and summarizes content. Built with FastAPI, LangGraph, ChromaDB, Groq Whisper STT, and gTTS.

## Key Features

- Hybrid RAG + Generative Interview
  - Phase 1: RAG-based document analysis (skills, experience, projects)
  - Phase 2: Generative, context-aware interview questions (one at a time)
  - Follow-ups with feedback and progressive difficulty
- RAG Q&A: Ask factual questions grounded in your uploaded PDF(s)
- Summarization: Structured summaries with headings and bullet points
- Robust error handling: Graceful fallbacks when Gemini API rate limits (429) occur
- Modular architecture: Clean separation across small focused modules

## Architecture (services/)

- `orchestrator.py` – Conversation flow controller (LangGraph)
- `intent_classifier.py` – Keyword-based routing (interview/continue/end/summary/rag)
- `document_analyzer.py` – RAG utilities (retriever + analysis)
- `interview_engine.py` – Hybrid interview logic (RAG + generative)
- `summary_engine.py` – Summarization engine
- `flow_manager.py` – Flow adapter layer
- `rag_pipeline.py` – RetrievalQA with rate-limit aware fallbacks
- `llm.py` – Gemini client factory

## API Endpoints

- POST `/upload/upload_pdf/` – Upload a PDF; stores Cloudinary URL and creates embeddings
- POST `/flow/ask` – Single unified endpoint for interview/summary/rag flows
- POST `/api/v1/stt` – Speech-to-text (Groq Whisper)
- POST `/api/v1/tts` – Text-to-speech (gTTS)
- GET `/` – Health status

### Flow: /flow/ask

Start a document-aware interview:

```json
POST /flow/ask
{
  "file_id": 12,
  "question": "interview me based on my resume"
}
```

Continue the interview (send user's answer and session ID from previous response):

```json
POST /flow/ask
{
  "file_id": 12,
  "question": "I optimized a Django app by caching ORM-heavy endpoints…",
  "conversation_session_id": "a1b2c3d4"
}
```

End the interview:

```json
POST /flow/ask
{
  "file_id": 12,
  "question": "end interview",
  "conversation_session_id": "a1b2c3d4"
}
```

Ask a factual question (RAG):

```json
POST /flow/ask
{
  "file_id": 12,
  "question": "What databases are mentioned in the document?"
}
```

Generate a summary:

```json
POST /flow/ask
{
  "file_id": 12,
  "question": "Give me a summary"
}
```

## Quick Start (macOS/zsh)

1) Create venv and install dependencies

```zsh
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2) Configure environment variables (`backend/.env`)

```env
# LLM
GOOGLE_API_KEY=your_google_api_key

# Speech-to-Text (Groq Whisper)
GROQ_API_KEY=your_groq_api_key

# Cloudinary (for PDF storage)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
```

3) Run the API

```zsh
uvicorn main:app --reload
```

## Request/Response Examples

Response from `/flow/ask` starting an interview:

```json
{
  "intent": "interview",
  "answer": "Perfect! I've analyzed your document... Please share your thoughts and reasoning.",
  "conversation_session_id": "a1b2c3d4",
  "requires_response": true,
  "conversation_state": "active_interview"
}
```

Continuation responses will keep `conversation_session_id` and may include brief feedback plus the next question.

## Notes & Troubleshooting

- Gemini 429 quota exceeded: The system detects rate-limit errors and returns helpful fallbacks (generic but relevant interview questions, or guidance to retry later for summaries/RAG)
- STT formats: Accepts common audio types (wav/webm/mp3/m4a)
- Vector DB: Uses local ChromaDB; no extra services required

## Dependency compatibility: Gemini packages

This project uses `langchain-google-genai` via LangChain. Avoid installing `google-generativeai` alongside it in the same env to prevent `google-ai-generativelanguage` version conflicts. If you must, isolate in a separate venv.

```zsh
source venv/bin/activate
pip uninstall -y google-generativeai
pip install -r requirements.txt
```


