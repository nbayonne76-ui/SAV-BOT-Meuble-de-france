# backend/app/services/cloudinary_storage.py
"""
Cloudinary storage service for handling file uploads to cloud storage
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Dict, Any, Optional
import logging
import asyncio
from functools import partial

from app.core.config import settings
from app.core.circuit_breaker import CircuitBreakerManager, CircuitBreakerError

logger = logging.getLogger(__name__)


class CloudinaryService:
    """Service for uploading files to Cloudinary"""

    _initialized = False

    @classmethod
    def initialize(cls):
        """Initialize Cloudinary with credentials from settings"""
        if cls._initialized:
            return

        if not settings.USE_CLOUDINARY:
            logger.warning(
                "Cloudinary credentials not configured. "
                "File uploads will not work in production."
            )
            return

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )

        cls._initialized = True
        logger.info(f"Cloudinary initialized for cloud: {settings.CLOUDINARY_CLOUD_NAME}")

    @classmethod
    async def upload_file(
        cls,
        file_path: str,
        folder: str = "sav-uploads",
        public_id: Optional[str] = None,
        resource_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Upload a file to Cloudinary

        Args:
            file_path: Path to the file to upload
            folder: Cloudinary folder to upload to
            public_id: Optional custom public ID for the file
            resource_type: Type of resource (auto, image, video, raw)

        Returns:
            Dict with upload result including URL and public_id

        Raises:
            Exception if upload fails
        """
        if not cls._initialized:
            cls.initialize()

        if not settings.USE_CLOUDINARY:
            raise Exception("Cloudinary not configured")

        try:
            # Upload to Cloudinary in a thread pool with circuit breaker protection
            loop = asyncio.get_event_loop()

            # Get circuit breaker for Cloudinary
            cloudinary_breaker = CircuitBreakerManager.get_breaker(
                name="cloudinary",
                failure_threshold=5,
                recovery_timeout=60,
                timeout=30
            )

            async def upload_to_cloudinary():
                return await loop.run_in_executor(
                    None,
                    partial(
                        cloudinary.uploader.upload,
                        file_path,
                        folder=folder,
                        public_id=public_id,
                        resource_type=resource_type,
                        unique_filename=True if not public_id else False,
                        overwrite=False
                    )
                )

            try:
                result = await cloudinary_breaker.call(upload_to_cloudinary)

                secure_url = result.get("secure_url")
                logger.info(f"File uploaded to Cloudinary: {result.get('public_id')}")
                logger.info(f"Cloudinary URL: {secure_url}")

                return {
                    "url": secure_url,
                    "public_id": result.get("public_id"),
                    "format": result.get("format"),
                    "resource_type": result.get("resource_type"),
                    "size": result.get("bytes"),
                    "width": result.get("width"),
                    "height": result.get("height")
                }

            except CircuitBreakerError as e:
                logger.error(f"Cloudinary circuit breaker is open: {e}")
                raise Exception(
                    "Service de stockage d'images temporairement indisponible. "
                    "Veuillez réessayer dans quelques instants."
                )

        except Exception as e:
            logger.error(f"Cloudinary upload failed: {str(e)}")
            raise Exception(f"Failed to upload file to Cloudinary: {str(e)}")

    @classmethod
    async def delete_file(cls, public_id: str, resource_type: str = "image") -> bool:
        """
        Delete a file from Cloudinary

        Args:
            public_id: The public ID of the file to delete
            resource_type: Type of resource (image, video, raw)

        Returns:
            True if deletion was successful
        """
        if not cls._initialized:
            cls.initialize()

        if not settings.USE_CLOUDINARY:
            return False

        try:
            # Run synchronous Cloudinary delete in thread pool with circuit breaker
            loop = asyncio.get_event_loop()

            # Get circuit breaker for Cloudinary
            cloudinary_breaker = CircuitBreakerManager.get_breaker(
                name="cloudinary",
                failure_threshold=5,
                recovery_timeout=60,
                timeout=30
            )

            async def delete_from_cloudinary():
                return await loop.run_in_executor(
                    None,
                    partial(
                        cloudinary.uploader.destroy,
                        public_id,
                        resource_type=resource_type
                    )
                )

            try:
                result = await cloudinary_breaker.call(delete_from_cloudinary)

                success = result.get("result") == "ok"
                if success:
                    logger.info(f"File deleted from Cloudinary: {public_id}")
                else:
                    logger.warning(f"Failed to delete file from Cloudinary: {public_id}")

                return success

            except CircuitBreakerError as e:
                logger.error(f"Cloudinary circuit breaker is open: {e}")
                return False

        except Exception as e:
            logger.error(f"Cloudinary deletion failed: {str(e)}")
            return False

    @classmethod
    def get_upload_url(
        cls,
        public_id: str,
        transformation: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get a URL for an uploaded file with optional transformations

        Args:
            public_id: The public ID of the file
            transformation: Optional transformation parameters

        Returns:
            URL to the file
        """
        if not cls._initialized:
            cls.initialize()

        return cloudinary.CloudinaryImage(public_id).build_url(
            transformation=transformation,
            secure=True
        )
