from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.upload import UploadResponse
from app.services.upload_service import process_uploaded_txt_file

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload-txt", response_model=UploadResponse)
async def upload_txt(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    if not file.filename.lower().endswith(".txt"):
        raise HTTPException(
            status_code=400, detail="Only .txt files are supported")

    try:
        result = await process_uploaded_txt_file(file)
        return UploadResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Failed to process uploaded file") from exc
