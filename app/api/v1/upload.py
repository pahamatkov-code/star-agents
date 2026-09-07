# app/api/v1/upload.py
import os
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status

logger = logging.getLogger("star_agents")

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "application/pdf", "text/plain"]

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    # 1. Перевірка MIME-типу
    if file.content_type not in ALLOWED_MIME_TYPES:
        logger.warning("Rejected upload for file %s: Invalid content-type %s", file.filename, file.content_type)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Unsupported file type: {file.content_type}"
        )

    # 2. Генерація унікального імені (UUIDv4)
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 3. Попотокове збереження та контроль розміру
    try:
        size = 0
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # Chunks по 1MB
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    os.remove(file_path)  # Видаляємо частинки файлу
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File size exceeds maximum allowed limit (10MB)"
                    )
                buffer.write(chunk)
                
        logger.info(
            "File upload success: original='%s', saved='%s', mime='%s', size=%d bytes",
            file.filename, unique_filename, file.content_type, size
        )
        return {
            "detail": "File uploaded successfully",
            "original_name": file.filename,
            "saved_name": unique_filename,
            "path": file_path,
            "size": size,
            "mime_type": file.content_type
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Upload failed for %s: %s", file.filename, str(e), exc_info=True)
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Internal server upload error")