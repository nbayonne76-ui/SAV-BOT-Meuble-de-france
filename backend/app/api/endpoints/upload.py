# backend/app/api/endpoints/upload.py
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from typing import List
import logging
import aiofiles
import os
from pathlib import Path
from datetime import datetime
import tempfile
from uuid import uuid4
from app.core.config import settings
from app.services.cloudinary_storage import CloudinaryService

logger = logging.getLogger(__name__)
router = APIRouter(redirect_slashes=False)

# Initialize Cloudinary
CloudinaryService.initialize()

# Create upload directories (fallback for local development)
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
PHOTOS_DIR = UPLOAD_DIR / "photos"
VIDEOS_DIR = UPLOAD_DIR / "videos"

for directory in [UPLOAD_DIR, PHOTOS_DIR, VIDEOS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return extension in settings.allowed_extensions_list

def get_file_directory(filename: str) -> Path:
    """Get the appropriate directory for the file"""
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if extension in ['mp4', 'mov', 'avi']:
        return VIDEOS_DIR
    return PHOTOS_DIR

# Upload handler (shared between routes with and without trailing slash)
async def _upload_files_handler(files: List[UploadFile]):
    """
    Upload photos or videos to Cloudinary (production) or local storage (development)
    """
    try:
        logger.info(f"Upload request received: {len(files)} file(s)")

        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucun fichier fourni"
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

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
            # new_filename = f"{timestamp}_{file.filename}"
            new_filename = f"{timestamp}_{uuid4().hex}_{file.filename}"
            # Upload to Cloudinary if configured, otherwise use local storage
            if settings.USE_CLOUDINARY:
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

            else:
                # Local storage fallback (development)
                file_dir = get_file_directory(file.filename)
                file_path = file_dir / new_filename

                async with aiofiles.open(str(file_path), 'wb') as f:
                    await f.write(content)

                logger.info(f"File saved locally: {file_path}")

                uploaded_files.append({
                    "original_name": file.filename,
                    "saved_name": new_filename,
                    "url": f"/uploads/{file_dir.name}/{new_filename}",
                    "size": len(content),
                    "type": extension,
                    "storage": "local"
                })

        return {
            "success": True,
            "files": uploaded_files,
            "count": len(uploaded_files)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload: {str(e)}"
        )
    finally:
        await file.close()

# Route with trailing slash
@router.post("/", status_code=status.HTTP_200_OK)
async def upload_files_with_slash(files: List[UploadFile] = File(...)):
    """Upload files (with trailing slash)"""
    return await _upload_files_handler(files)

# Route without trailing slash (fixes 307 redirect issue)
@router.post("", status_code=status.HTTP_200_OK)
async def upload_files_without_slash(files: List[UploadFile] = File(...)):
    """Upload files (without trailing slash)"""
    return await _upload_files_handler(files)

@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_upload_stats():
    """Get upload statistics"""
    try:
        photos_count = len(list(PHOTOS_DIR.glob("*")))
        videos_count = len(list(VIDEOS_DIR.glob("*")))

        return {
            "success": True,
            "stats": {
                "photos": photos_count,
                "videos": videos_count,
                "total": photos_count + videos_count
            }
        }
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )
