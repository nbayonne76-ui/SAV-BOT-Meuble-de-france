# backend/app/api/endpoints/upload.py
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from typing import List
import logging
import tempfile
import os
from datetime import datetime
from app.core.config import settings
from app.services.cloudinary_storage import CloudinaryService

logger = logging.getLogger(__name__)
router = APIRouter()

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return extension in settings.allowed_extensions_list

@router.post("/", status_code=status.HTTP_200_OK)
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload photos or videos to Cloudinary
    """
    try:
        logger.info(f"Upload request received: {len(files)} file(s)")

        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucun fichier fourni"
            )

        if not settings.USE_CLOUDINARY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cloudinary not configured. Please contact administrator."
            )

        uploaded_files = []

        for file in files:
            # Validate file
            if not is_allowed_file(file.filename):
                logger.warning(f"Invalid file type: {file.filename}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Type de fichier non autorisé: {file.filename}"
                )

            # Check file size
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Fichier trop volumineux: {file.filename} (max {settings.MAX_FILE_SIZE / 1024 / 1024}MB)"
                )

            # Determine file type
            extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'

            # Save to temporary file first
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name

            try:
                # Upload to Cloudinary
                resource_type = "video" if extension in ['mp4', 'mov', 'avi', 'webm'] else "image"
                result = await CloudinaryService.upload_file(
                    tmp_path,
                    folder="sav-uploads",
                    resource_type=resource_type
                )

                logger.info(f"File uploaded to Cloudinary: {result['public_id']}")

                uploaded_files.append({
                    "original_name": file.filename,
                    "saved_name": result['public_id'],
                    "url": result['url'],
                    "size": len(content),
                    "type": extension,
                    "storage": "cloudinary"
                })

            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass

        return {
            "success": True,
            "files": uploaded_files,
            "count": len(uploaded_files)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )

@router.get("/health", status_code=status.HTTP_200_OK)
async def upload_health():
    """Check upload service health"""
    return {
        "success": True,
        "storage": "cloudinary" if settings.USE_CLOUDINARY else "local",
        "configured": settings.USE_CLOUDINARY
    }
