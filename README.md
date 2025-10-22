# 🎤 AI Voice Assistant with Hybrid RAG + Generative Interview

Talk to your documents. Upload a PDF, then have natural voice conversations: ask factual questions, get summaries, or take a tailored mock interview based on your resume. Built with React (Vite) and FastAPI, powered by ChromaDB, Groq Whisper (STT), gTTS (TTS), and Google Gemini.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![React](https://img.shields.io/badge/React-18+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)

## ✨ Highlights

- Hybrid RAG + Generative Reasoning for interviews:
  - RAG analyzes your document (skills, experience, projects)
  - Generative model creates one high‑quality interview question at a time
  - Follow‑up questions include brief feedback and vary by topic
- Unified flow endpoint: `/flow/ask` handles interview, summary, and RAG
- Graceful rate‑limit handling (Gemini 429): helpful fallbacks keep the app usable
- Modular backend architecture for maintainability

## ⚙️ System Overview

Backend (FastAPI):

- `routers/flow.py` – POST `/flow/ask` single entrypoint
- `routers/uploads.py` – PDF uploads → Cloudinary + embeddings
- `stt_services/` – Groq Whisper STT: POST `/api/v1/stt`
- `tts_service/` – gTTS speech: POST `/api/v1/tts`

Services (modular):

- `orchestrator.py` – Simple controller (no LangGraph)
- `intent_classifier.py` – Keyword routing (interview/continue/end/summary/rag)
- `document_analyzer.py` – RAG helpers (retriever + analysis)
- `interview_engine.py` – Hybrid interview generation
- `summary_engine.py` – Structured document summaries
- `rag_pipeline.py` – RetrievalQA with rate‑limit aware fallbacks

Frontend (React + Vite):

- Voice mic control, waveform visuals, and clean UI
- Hooks and utilities in `src/hooks/useVoiceAssistant.js` and `src/utils/api.js`

## 🚀 Quick Start

Prereqs: Node 18+, Python 3.10+, ffmpeg (optional for TTS speed), Cloudinary account.

1) Backend setup

```zsh
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
```

Run backend:

```zsh
uvicorn main:app --reload
```

2) Frontend setup

```zsh
cd frontend
npm install
npm run dev
```

Optional frontend env (create `frontend/.env.local`):

```env
VITE_BACKEND_URL=http://localhost:8000
# Increase if large PDFs or slow networks cause timeouts (ms)
VITE_UPLOAD_TIMEOUT_MS=120000
```

Access:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

## 📡 API Cheat‑Sheet

Upload PDF and create embeddings:

```http
POST /upload/upload_pdf/
Content-Type: multipart/form-data
file: <your.pdf>
```

Unified flow (interview/summary/rag):

```json
POST /flow/ask
{
  "file_id": 12,
  "question": "interview me based on my resume"
}
```

Continue interview:

```json
POST /flow/ask
{
  "file_id": 12,
  "question": "I built a scalable service on Django and optimized queries…",
  "conversation_session_id": "a1b2c3d4"
}
```

End interview:

```json
POST /flow/ask
{
  "file_id": 12,
  "question": "end interview",
  "conversation_session_id": "a1b2c3d4"
}
```

STT / TTS:

- `POST /api/v1/stt` – multipart `file`
- `POST /api/v1/tts` – JSON `{ text: string, speed?: number }`

## 🧠 How Interviews Work (Hybrid)

1) RAG analyzes your doc → extracts skills, experience, areas, projects
2) Generative model crafts a single tailored question (no answers)
3) Your reply → brief feedback + a different follow‑up question
4) Say “end interview” to wrap up with a professional closing

If Gemini hits rate limits, you’ll still get thoughtful fallback questions and guidance.

## 🧩 Project Structure (condensed)

```
backend/
  routers/           # flow.py, uploads.py
  services/
    orchestrator.py  # LangGraph controller
    intent_classifier.py
    document_analyzer.py
    interview_engine.py
    summary_engine.py
    flow_manager.py
    rag_pipeline.py
  stt_services/      # routes.py, app.py, whisper_model.py
  tts_service/       # routes.py, app.py, tts_model.py, schema.py
  models/, db/, utils/, main.py

frontend/
  src/components, hooks, utils, App.jsx, main.jsx
```

## 🛡️ Troubleshooting

- Gemini quota: If you see 429 or quota errors, the backend returns useful fallback messages and keeps working; try again after the quota resets.
- Audio types: The STT endpoint accepts wav/webm/mp3/m4a.
- Embeddings empty: If your PDF has no extractable text, embeddings won’t be created; you can still upload another PDF.

## 📜 License

MIT. See LICENSE.
