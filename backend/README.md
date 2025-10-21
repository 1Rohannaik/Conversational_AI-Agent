# AI Appointment Reminder System

This backend scaffolds a production-ready, async voice agent that calls patients to confirm or reschedule appointments, integrates with your existing STT/TTS services, and persists progress with checkpoints.

## Components
- Orchestrator: `backend/orchestrator/runner.py` (FastAPI, Twilio webhooks)
- STT: `backend/stt_services/app.py` (already present)
- TTS: `backend/tts_service/app.py` (already present)
- DB models: `backend/db/models.py`, session: `backend/db/session.py`
- Workflow: `backend/workflow/langgraph.json`
- Intent detection: `backend/orchestrator/intents.py`
- RAG template: `backend/rag/async_retriever.py`
- Queue: `backend/queue/celery_app.py`
- Prompts: `backend/prompts/system_prompt.txt`

## Quick start (dev)
1. Create and activate a virtual environment, then install deps:

```zsh
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

2. Set environment variables (copy `.env.example` then edit):

```zsh
cp backend/.env.example backend/.env
# Edit backend/.env with your values
export DATABASE_URL="sqlite+aiosqlite:///./backend/dev.db"
export TTS_BASE_URL="http://localhost:8001"   # your TTS service
export STT_BASE_URL="http://localhost:8002"   # your STT service
export PUBLIC_BASE_URL="http://localhost:8000"
export TWILIO_ACCOUNT_SID="AC..."
export TWILIO_AUTH_TOKEN="..."
export TWILIO_FROM_NUMBER="+1..."
export REDIS_URL="redis://localhost:6379/0"
```

3. Run services in separate terminals:

- TTS:
```zsh
uvicorn backend.tts_service.app:app --host 0.0.0.0 --port 8001 --reload
```
- STT:
```zsh
uvicorn backend.stt_services.app:app --host 0.0.0.0 --port 8002 --reload
```
- Orchestrator:
```zsh
uvicorn backend.orchestrator.runner:app --host 0.0.0.0 --port 8000 --reload
```
- Celery worker (optional queue):
```zsh
celery -A backend.queue.celery_app.celery_app worker --loglevel=info
```

4. Seed a patient (SQLite):

```zsh
python - <<'PY'
import asyncio
from datetime import datetime, timedelta
from backend.db.session import engine, AsyncSessionLocal
from backend.db.models import Base, Patient

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as s:
        p = Patient(name="John Doe", phone_e164="+15551234567",
                    last_visit=datetime.utcnow()-timedelta(days=45),
                    last_illness="flu", next_appointment=datetime.utcnow()+timedelta(days=2))
        s.add(p)
        await s.commit()

asyncio.run(main())
PY
```

4b. Alternatively, import from CSV:

```zsh
python -m backend.tools.import_patients backend/tools/patients.sample.csv
```

CSV columns (required: name, phone_e164):
- name: Patient full name
- phone_e164: E.164 format number, e.g., +15551234567
- last_visit: optional date/time (e.g., 2025-09-01 or 2025-09-01 10:00:00)
- last_illness: optional text
- next_appointment: optional date/time (same formats)
- opt_out: true/false

5. Start a call (simulate):

```zsh
curl -s -X POST http://localhost:8000/orchestrator/start \
  -H 'Content-Type: application/json' \
  -d '{"patient_id": 1}' | jq
```

Twilio will hit `/orchestrator/voice/answer` and the flow proceeds via `<Gather input="speech">`.

## Notes
- Replace Chroma with Qdrant/Pinecone in `backend/rag/async_retriever.py` for production and add proper async LLM calls.
- Add encryption at rest (pgcrypto or application-level) for PII if using Postgres.
- Enforce call-time windows and audit logging in orchestrator before placing calls.

## Dependency compatibility: Gemini packages
This project uses `langchain-google-genai` (via LangChain) to access Gemini models. You don't need the standalone `google-generativeai` SDK. Installing both can lead to version conflicts around `google-ai-generativelanguage`.

If you see a warning like:

```
google-generativeai 0.8.x requires google-ai-generativelanguage==0.6.10, but you have 0.6.18 which is incompatible.
```

Resolution (recommended):
- Remove `google-generativeai` from your environment and keep `langchain-google-genai` only.

Commands (from repo root):

```zsh
source backend/venv/bin/activate
pip uninstall -y google-generativeai
pip install -r backend/requirements.txt
```

If you explicitly need the `google-generativeai` SDK in your own code, avoid installing `langchain-google-genai` at the same time to prevent resolver conflicts, or isolate it in a separate virtual environment.

