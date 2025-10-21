from fastapi import APIRouter, status
from .schema import TTSRequest
from .app import tts_endpoint


router = APIRouter()

@router.post("/api/v1/tts", status_code=status.HTTP_200_OK)
async def get_tts_endpoint(req: TTSRequest):
    return await tts_endpoint(req)