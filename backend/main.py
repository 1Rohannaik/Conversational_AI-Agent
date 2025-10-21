from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import uploads
from routers import qa
from routers import flow
from routers import db_health
from routers import interview
from routers import conversation
from db.session import engine
from models import Base  # ensures models are imported and metadata available
from stt_services.routes import router as stt_router
from tts_service.routes import router as tts_router

app = FastAPI(title="Gemini Voice RAG Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(uploads.router)
app.include_router(qa.router)
app.include_router(flow.router)
# app.include_router(chat.router)
app.include_router(interview.router)
app.include_router(conversation.router)
app.include_router(stt_router)
app.include_router(tts_router)
app.include_router(db_health.router)

# Create tables on startup if they don't exist
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/test")
def test():
    return {"message": "Backend is working!", "timestamp": "2025-10-21"}
