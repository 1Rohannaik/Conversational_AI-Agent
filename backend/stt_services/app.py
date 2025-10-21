from fastapi import UploadFile, File, APIRouter
from fastapi.responses import JSONResponse
import tempfile, os, pathlib
from .whisper_model import transcribe_audio_with_groq 

router = APIRouter()

async def stt_endpoint(file: UploadFile = File(...)):
    # Choose suffix based on uploaded filename or content type
    suffix = '.wav'
    if file.filename and '.' in file.filename:
        suffix = '.' + file.filename.rsplit('.', 1)[-1].lower()
    elif file.content_type:
        if 'webm' in file.content_type:
            suffix = '.webm'
        elif 'mp3' in file.content_type:
            suffix = '.mp3'
        elif 'm4a' in file.content_type or 'mp4' in file.content_type:
            suffix = '.m4a'

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    try:
        text = transcribe_audio_with_groq(path)
        return JSONResponse({"transcript": text})
    finally:
        os.remove(path)
