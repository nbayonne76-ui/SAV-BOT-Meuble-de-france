# backend/app/services/storage.py
"""
File storage abstraction service.
Supports local filesystem storage with optional cloud storage (S3-compatible) extension.
"""
import os
import logging
import shutil
import hashlib
import mimetypes
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import uuid
import aiofiles
import aiofiles.os

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class FileMetadata:
    """Metadata for a stored file."""
    file_id: str
    original_filename: str
    stored_filename: str
    content_type: str
    size_bytes: int
    checksum: str
    storage_path: str
    upload_timestamp: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    category: str = "general"
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class BaseStorage(ABC):
    """Abstract base class for storage implementations."""

    @abstractmethod
    async def save(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        category: str = "general",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> FileMetadata:
        """Save a file to storage."""
        pass

    @abstractmethod
    async def get(self, file_id: str) -> Optional[Tuple[bytes, FileMetadata]]:
        """Get a file by ID."""
        pass

    @abstractmethod
    async def delete(self, file_id: str) -> bool:
        """Delete a file."""
        pass

    @abstractmethod
    async def exists(self, file_id: str) -> bool:
        """Check if a file exists."""
        pass

    @abstractmethod
    async def get_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """Get file metadata without the file content."""
        pass

    @abstractmethod
    async def list_files(
        self,
        category: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 100
    ) -> List[FileMetadata]:
        """List files with optional filters."""
        pass

    @abstractmethod
    async def cleanup_old_files(self, max_age_days: int = 30) -> int:
        """Clean up files older than max_age_days."""
        pass


class LocalStorage(BaseStorage):
    """
    Local filesystem storage implementation.
    Files are organized by category (photos, videos, documents, etc.)
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize local storage.

        Args:
            base_path: Base directory for file storage
        """
        self.base_path = Path(base_path or settings.UPLOAD_DIR).resolve()
        self._metadata_dir = self.base_path / ".metadata"

        # Create necessary directories
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._metadata_dir.mkdir(parents=True, exist_ok=True)

        # Create category directories
        for category in ["photos", "videos", "documents", "temp"]:
            (self.base_path / category).mkdir(exist_ok=True)

        logger.info(f"Local storage initialized at: {self.base_path}")

    def _generate_file_id(self) -> str:
        """Generate a unique file ID."""
        return str(uuid.uuid4())

    def _get_safe_filename(self, original_filename: str, file_id: str) -> str:
        """Generate a safe filename for storage."""
        # Get file extension
        ext = Path(original_filename).suffix.lower()
        # Create safe filename: id + extension
        return f"{file_id}{ext}"

    def _compute_checksum(self, data: bytes) -> str:
        """Compute SHA-256 checksum of file data."""
        return hashlib.sha256(data).hexdigest()

    def _get_category_path(self, category: str) -> Path:
        """Get the path for a category."""
        # Sanitize category name
        safe_category = "".join(c for c in category if c.isalnum() or c in "_-")
        if not safe_category:
            safe_category = "general"

        category_path = self.base_path / safe_category
        category_path.mkdir(exist_ok=True)
        return category_path

    def _get_metadata_path(self, file_id: str) -> Path:
        """Get the path for file metadata."""
        return self._metadata_dir / f"{file_id}.json"

    async def _save_metadata(self, metadata: FileMetadata) -> None:
        """Save file metadata to disk."""
        import json
        metadata_path = self._get_metadata_path(metadata.file_id)
        async with aiofiles.open(metadata_path, 'w') as f:
            await f.write(json.dumps(metadata.to_dict(), indent=2))

    async def _load_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """Load file metadata from disk."""
        import json
        metadata_path = self._get_metadata_path(file_id)

        if not metadata_path.exists():
            return None

        try:
            async with aiofiles.open(metadata_path, 'r') as f:
                data = json.loads(await f.read())
                return FileMetadata(**data)
        except Exception as e:
            logger.error(f"Error loading metadata for {file_id}: {e}")
            return None

    async def save(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        category: str = "general",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> FileMetadata:
        """
        Save a file to local storage.

        Args:
            file: File-like object to save
            filename: Original filename
            content_type: MIME type
            category: Storage category (photos, videos, etc.)
            user_id: Optional user ID
            session_id: Optional session ID
            metadata: Optional additional metadata

        Returns:
            FileMetadata for the saved file
        """
        # Generate unique ID and safe filename
        file_id = self._generate_file_id()
        stored_filename = self._get_safe_filename(filename, file_id)

        # Get storage path
        category_path = self._get_category_path(category)
        file_path = category_path / stored_filename

        # Read file data
        file_data = file.read()
        if hasattr(file, 'seek'):
            file.seek(0)

        # Compute checksum
        checksum = self._compute_checksum(file_data)

        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data)

        # Create metadata
        file_metadata = FileMetadata(
            file_id=file_id,
            original_filename=filename,
            stored_filename=stored_filename,
            content_type=content_type,
            size_bytes=len(file_data),
            checksum=checksum,
            storage_path=str(file_path.relative_to(self.base_path)),
            upload_timestamp=datetime.utcnow().isoformat(),
            user_id=user_id,
            session_id=session_id,
            category=category,
            metadata=metadata or {}
        )

        # Save metadata
        await self._save_metadata(file_metadata)

        logger.info(f"File saved: {file_id} ({filename}, {len(file_data)} bytes)")
        return file_metadata

    async def get(self, file_id: str) -> Optional[Tuple[bytes, FileMetadata]]:
        """
        Get a file by ID.

        Args:
            file_id: File identifier

        Returns:
            Tuple of (file_data, metadata) or None if not found
        """
        metadata = await self._load_metadata(file_id)
        if not metadata:
            return None

        file_path = self.base_path / metadata.storage_path

        if not file_path.exists():
            logger.warning(f"File not found on disk: {file_id}")
            return None

        try:
            async with aiofiles.open(file_path, 'rb') as f:
                file_data = await f.read()
            return file_data, metadata
        except Exception as e:
            logger.error(f"Error reading file {file_id}: {e}")
            return None

    async def delete(self, file_id: str) -> bool:
        """
        Delete a file.

        Args:
            file_id: File identifier

        Returns:
            True if deleted, False if not found
        """
        metadata = await self._load_metadata(file_id)
        if not metadata:
            return False

        file_path = self.base_path / metadata.storage_path
        metadata_path = self._get_metadata_path(file_id)

        try:
            # Delete file
            if file_path.exists():
                await aiofiles.os.remove(file_path)

            # Delete metadata
            if metadata_path.exists():
                await aiofiles.os.remove(metadata_path)

            logger.info(f"File deleted: {file_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return False

    async def exists(self, file_id: str) -> bool:
        """Check if a file exists."""
        metadata = await self._load_metadata(file_id)
        if not metadata:
            return False

        file_path = self.base_path / metadata.storage_path
        return file_path.exists()

    async def get_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """Get file metadata without the file content."""
        return await self._load_metadata(file_id)

    async def list_files(
        self,
        category: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 100
    ) -> List[FileMetadata]:
        """
        List files with optional filters.

        Args:
            category: Filter by category
            user_id: Filter by user ID
            session_id: Filter by session ID
            limit: Maximum number of files to return

        Returns:
            List of FileMetadata
        """
        files = []

        # Iterate through metadata files
        for metadata_file in self._metadata_dir.glob("*.json"):
            if len(files) >= limit:
                break

            file_id = metadata_file.stem
            metadata = await self._load_metadata(file_id)

            if not metadata:
                continue

            # Apply filters
            if category and metadata.category != category:
                continue
            if user_id and metadata.user_id != user_id:
                continue
            if session_id and metadata.session_id != session_id:
                continue

            files.append(metadata)

        # Sort by upload timestamp (newest first)
        files.sort(key=lambda x: x.upload_timestamp, reverse=True)
        return files[:limit]

    async def cleanup_old_files(self, max_age_days: int = 30) -> int:
        """
        Clean up files older than max_age_days.

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of files cleaned up
        """
        cutoff = datetime.utcnow() - timedelta(days=max_age_days)
        cutoff_str = cutoff.isoformat()
        cleaned = 0

        for metadata_file in self._metadata_dir.glob("*.json"):
            file_id = metadata_file.stem
            metadata = await self._load_metadata(file_id)

            if metadata and metadata.upload_timestamp < cutoff_str:
                if await self.delete(file_id):
                    cleaned += 1

        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} old files (older than {max_age_days} days)")

        return cleaned

    def get_public_url(self, file_id: str) -> Optional[str]:
        """
        Get the public URL for a file.
        For local storage, returns the relative path for serving.

        Args:
            file_id: File identifier

        Returns:
            URL path or None if file not found
        """
        # This is synchronous for simplicity
        metadata_path = self._get_metadata_path(file_id)
        if not metadata_path.exists():
            return None

        import json
        with open(metadata_path) as f:
            metadata = json.load(f)

        return f"/uploads/{metadata['storage_path']}"


class StorageManager:
    """
    Singleton storage manager that provides the appropriate storage implementation.
    """

    _instance: Optional['StorageManager'] = None
    _storage: Optional[BaseStorage] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialize(
        cls,
        storage_type: str = "local",
        **kwargs
    ) -> 'StorageManager':
        """
        Initialize the storage manager.

        Args:
            storage_type: Type of storage ('local' or future 's3')
            **kwargs: Additional arguments for storage backend

        Returns:
            StorageManager instance
        """
        instance = cls()

        if storage_type == "local":
            instance._storage = LocalStorage(kwargs.get("base_path"))
        # Future: Add S3 support
        # elif storage_type == "s3":
        #     instance._storage = S3Storage(**kwargs)
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")

        return instance

    @classmethod
    def get_storage(cls) -> BaseStorage:
        """
        Get the storage instance.

        Returns:
            BaseStorage instance

        Raises:
            RuntimeError: If storage is not initialized
        """
        instance = cls()
        if instance._storage is None:
            # Auto-initialize with local storage
            cls.initialize()
        return instance._storage


# Convenience function
def get_storage() -> BaseStorage:
    """Get the storage instance."""
    return StorageManager.get_storage()
