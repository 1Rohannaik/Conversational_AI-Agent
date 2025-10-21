from fastapi import APIRouter, UploadFile, status
from fastapi.params import File
from .app import stt_endpoint

router = APIRouter()

@router.post("/api/v1/stt", status_code=status.HTTP_200_OK)
async def get_stt_endpoint(file: UploadFile = File(...)):
    return await stt_endpoint(file)
