# backend/app/api/endpoints/upload.py
"""
File upload endpoints with rate limiting and security controls
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Request, Depends
from typing import List
import logging
import tempfile
import os
import io
from datetime import datetime
from app.core.config import settings
from app.core.rate_limit import limiter, RateLimits
from app.services.cloudinary_storage import CloudinaryService
from app.services.storage import get_storage
from app.api.deps import optional_auth
from app.models.user import UserDB

logger = logging.getLogger(__name__)
router = APIRouter()

# Upload configuration limits
MAX_FILES_PER_REQUEST = 10  # Maximum files in a single upload request

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return extension in settings.allowed_extensions_list

@router.post("/", status_code=status.HTTP_200_OK)
@limiter.limit(RateLimits.UPLOAD_FILE)
async def upload_files(
    request: Request,
    files: List[UploadFile] = File(...),
    current_user: UserDB = Depends(optional_auth)
):
    """
    Upload photos or videos with rate limiting and security controls.

    Rate limited to 10 requests per minute.
    Maximum 10 files per request.
    Maximum file size: 10MB per file.
    """
    try:
        user_info = f"user:{current_user.username}" if current_user else "anonymous"
        logger.info(f"📤 Upload request from {user_info}: {len(files)} file(s)")

        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucun fichier fourni"
            )

        # Limit number of files per request to prevent abuse
        if len(files) > MAX_FILES_PER_REQUEST:
            logger.warning(f"⚠️ Upload rejected: too many files ({len(files)} > {MAX_FILES_PER_REQUEST})")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Trop de fichiers. Maximum: {MAX_FILES_PER_REQUEST} fichiers par requête"
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

            # Read content and check file size
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Fichier trop volumineux: {file.filename} (max {settings.MAX_FILE_SIZE / 1024 / 1024}MB)"
                )

            # Determine file type
            extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
            resource_type = "video" if extension in ['mp4', 'mov', 'avi', 'webm'] else "image"

            if settings.USE_CLOUDINARY:
                # Save to temporary file first (Cloudinary expects a file path)
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as tmp_file:
                    tmp_file.write(content)
                    tmp_path = tmp_file.name

                try:
                    # Upload to Cloudinary
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

            else:
                # Local storage fallback (development mode)
                try:
                    storage = get_storage()
                    file_obj = io.BytesIO(content)

                    # Save using storage (category 'photos' or 'videos')
                    metadata = await storage.save(
                        file_obj,
                        file.filename,
                        file.content_type or 'application/octet-stream',
                        category='photos' if resource_type == 'image' else 'videos'
                    )

                    public_url = storage.get_public_url(metadata.file_id)

                    uploaded_files.append({
                        "original_name": file.filename,
                        "saved_name": metadata.file_id,
                        "url": public_url,
                        "size": metadata.size_bytes,
                        "type": extension,
                        "storage": "local"
                    })

                    logger.info(f"File saved locally: {metadata.file_id} -> {public_url}")

                except Exception as e:
                    logger.error(f"Local storage save failed: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Erreur lors de l'enregistrement local du fichier: {str(e)}"
                    )

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
        "configured": settings.USE_CLOUDINARY,
        "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024),
        "max_files_per_request": MAX_FILES_PER_REQUEST,
        "allowed_extensions": settings.allowed_extensions_list
    }