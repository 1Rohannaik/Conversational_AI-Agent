from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.rag_pipeline import aask_question
from services.vectorstore import collection_name
from chromadb import PersistentClient
from chromadb.config import Settings as ChromaSettings

router = APIRouter(prefix="/qa", tags=["QA"])


class AskRequest(BaseModel):
    file_id: int
    question: str


@router.post("/ask")
async def ask(req: AskRequest):
    if not req.question or not str(req.question).strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        answer = await aask_question(str(req.file_id), req.question)
    except ValueError as ve:
        # Likely no embeddings/collection
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {e}")
    return {"answer": answer}


@router.get("/status/{file_id}")
async def qa_status(file_id: int):
    name = collection_name(str(file_id))
    client = PersistentClient(path="./chroma_db", settings=ChromaSettings(anonymized_telemetry=False))
    try:
        collections = client.list_collections()
        exists = any(getattr(c, "name", None) == name for c in collections)
        count = 0
        if exists:
            col = client.get_collection(name=name)
            if hasattr(col, "count"):
                count = col.count()
        return {"collection": name, "exists": exists, "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check QA status: {e}")
