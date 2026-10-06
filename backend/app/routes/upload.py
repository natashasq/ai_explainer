from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from typing import Optional

from app.schemas.upload import UploadResponse
from app.services.upload_service import process_uploaded_file

router = APIRouter(prefix="/api", tags=["upload"])

ALLOWED_EXTENSIONS = {".txt", ".pdf"}


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    existing_kb_id: Optional[str] = Form(None),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail="Only .txt and .pdf files are supported")

    try:
        result = await process_uploaded_file(file, existing_kb_id)
        return UploadResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Failed to process uploaded file") from exc
