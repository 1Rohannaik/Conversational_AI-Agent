from fastapi import FastAPI, UploadFile, File, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
import os
import uuid
from db.session import get_db
from models.pdf import PDFFile
from services.pdf_reader import extract_text_from_pdf
from PyPDF2.errors import PdfReadError
from services.rag_pipeline import astore_embeddings
from dotenv import load_dotenv
from utils.cloudinary import ensure_configured as ensure_cloudinary_config
from utils.cloudinary import config_status as cloudinary_config_status_util

router = APIRouter(prefix="/upload", tags=["Upload"])


def _configure_cloudinary_if_needed() -> None:
    try:
        ensure_cloudinary_config()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    _configure_cloudinary_if_needed()
    # Read file into memory once
    contents = await file.read()

    # Upload to Cloudinary
    result = cloudinary.uploader.upload(
        contents,
        resource_type="raw",
        public_id=f"pdfs/{file.filename.split('.')[0]}",
        unique_filename=False,
        overwrite=True,
        filename=file.filename,
    )

    # Save metadata in DB
    pdf_record = PDFFile(filename=file.filename, cloud_url=result["secure_url"])
    db.add(pdf_record)
    db.commit()
    db.refresh(pdf_record)

    # Save temporary file for text extraction
    temp_filename = f"temp_{uuid.uuid4()}.pdf"
    with open(temp_filename, "wb") as f:
        f.write(contents)

    # Extract text and store embeddings
    try:
        text = extract_text_from_pdf(temp_filename)
    except PdfReadError as e:
        # Cleanup and return a 400 error for invalid/corrupt PDFs
        os.remove(temp_filename)
        # Also delete the DB record since this PDF isn't usable for RAG
        db.delete(pdf_record)
        db.commit()
        raise HTTPException(status_code=400, detail=f"Invalid or corrupt PDF: {str(e)}")

    if not text.strip():
        # Cleanup temp file and skip embeddings if no text
        os.remove(temp_filename)
        return {
            "id": pdf_record.id,
            "url": pdf_record.cloud_url,
            "message": "PDF uploaded, but no extractable text was found (no embeddings created)",
        }

    # Offload embeddings to async wrapper so the event loop isn't blocked
    await astore_embeddings(text, str(pdf_record.id))

    # Remove temp file
    os.remove(temp_filename)

    return {
        "id": pdf_record.id,
        "url": pdf_record.cloud_url,
        "message": "PDF uploaded and embeddings stored successfully",
    }


@router.get("/config_status")
def cloudinary_config_status():
    return cloudinary_config_status_util()
