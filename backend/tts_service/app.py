from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import tempfile, os
from .tts_model import normalize_text, speed_up_wav, generate_tts
from .schema import TTSRequest
router = APIRouter()


async def tts_endpoint(req: TTSRequest):
    text = normalize_text(req.text)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp.close()
    generate_tts(text, tmp.name)
    out_path = speed_up_wav(tmp.name, req.speed)
    if out_path != tmp.name:
        os.remove(tmp.name)

    return FileResponse(out_path, media_type="audio/mpeg", filename="speech.mp3")


async def health():
    return {"status": "ok", "service": "tts-gtts", "version": "1.0.0"}
