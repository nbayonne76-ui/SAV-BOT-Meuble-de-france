# backend/app/services/session_manager.py
"""
Session management service for chat sessions.
Supports Redis for production and in-memory storage for development.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict, field

from app.core.redis import get_cache, cache_get_json, cache_set_json

logger = logging.getLogger(__name__)

# Session configuration
SESSION_TTL_HOURS = 24  # Sessions expire after 24 hours
SESSION_KEY_PREFIX = "session:"


@dataclass
class ConversationMessage:
    """A single message in the conversation history."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatSession:
    """
    Represents a chat session with all its data.
    """
    session_id: str
    user_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_active: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    # Conversation data
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    conversation_type: str = "general"
    language: str = "fr"

    # SAV-specific data
    order_number: Optional[str] = None
    sav_context: Dict[str, Any] = field(default_factory=dict)
    problem_detected: Optional[str] = None
    priority_score: Optional[float] = None

    # Evidence and files
    photos: List[str] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)

    # Session metadata
    message_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create session from dictionary."""
        return cls(**data)

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation history."""
        message = ConversationMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.conversation_history.append(asdict(message))
        self.message_count += 1
        self.last_active = datetime.utcnow().isoformat()

    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent messages."""
        return self.conversation_history[-limit:]

    def update_sav_context(self, **kwargs):
        """Update SAV-specific context."""
        self.sav_context.update(kwargs)
        self.last_active = datetime.utcnow().isoformat()


class SessionManager:
    """
    Manages chat sessions using Redis or in-memory cache.
    """

    def __init__(self):
        self._cache = None

    def _get_cache(self):
        """Get the cache instance lazily."""
        if self._cache is None:
            self._cache = get_cache()
        return self._cache

    def _session_key(self, session_id: str) -> str:
        """Generate the cache key for a session."""
        return f"{SESSION_KEY_PREFIX}{session_id}"

    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> ChatSession:
        """
        Create a new chat session.

        Args:
            session_id: Unique session identifier
            user_id: Optional user ID if authenticated
            metadata: Optional initial metadata

        Returns:
            Created ChatSession
        """
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {}
        )

        await self.save_session(session)
        logger.info(f"Created new session: {session_id}")
        return session

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            ChatSession if found, None otherwise
        """
        key = self._session_key(session_id)
        data = await cache_get_json(key)

        if data:
            logger.debug(f"Session found: {session_id}")
            return ChatSession.from_dict(data)

        logger.debug(f"Session not found: {session_id}")
        return None

    async def save_session(self, session: ChatSession) -> bool:
        """
        Save a session to cache.

        Args:
            session: ChatSession to save

        Returns:
            True if successful
        """
        key = self._session_key(session.session_id)
        ttl_seconds = SESSION_TTL_HOURS * 3600

        success = await cache_set_json(key, session.to_dict(), expire=ttl_seconds)

        if success:
            logger.debug(f"Session saved: {session.session_id}")
        else:
            logger.error(f"Failed to save session: {session.session_id}")

        return success

    async def get_or_create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> ChatSession:
        """
        Get an existing session or create a new one.

        Args:
            session_id: Session identifier
            user_id: Optional user ID
            metadata: Optional metadata for new sessions

        Returns:
            ChatSession (existing or new)
        """
        session = await self.get_session(session_id)

        if session:
            # Update last active time
            session.last_active = datetime.utcnow().isoformat()
            await self.save_session(session)
            return session

        return await self.create_session(session_id, user_id, metadata)

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        key = self._session_key(session_id)
        cache = self._get_cache()
        deleted = await cache.delete(key)

        if deleted:
            logger.info(f"Session deleted: {session_id}")
        else:
            logger.debug(f"Session not found for deletion: {session_id}")

        return deleted

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Optional[ChatSession]:
        """
        Add a message to a session's conversation history.

        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            metadata: Optional message metadata

        Returns:
            Updated ChatSession or None if session not found
        """
        session = await self.get_session(session_id)

        if not session:
            logger.warning(f"Cannot add message - session not found: {session_id}")
            return None

        session.add_message(role, content, metadata)
        await self.save_session(session)
        return session

    async def update_session(
        self,
        session_id: str,
        **updates
    ) -> Optional[ChatSession]:
        """
        Update session fields.

        Args:
            session_id: Session identifier
            **updates: Fields to update

        Returns:
            Updated ChatSession or None if not found
        """
        session = await self.get_session(session_id)

        if not session:
            return None

        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)

        session.last_active = datetime.utcnow().isoformat()
        await self.save_session(session)
        return session

    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List sessions, optionally filtered by user.

        Args:
            user_id: Optional user ID to filter by
            limit: Maximum number of sessions to return

        Returns:
            List of session summaries
        """
        cache = self._get_cache()
        keys = await cache.keys(f"{SESSION_KEY_PREFIX}*")

        sessions = []
        for key in keys[:limit]:
            session_id = key.replace(SESSION_KEY_PREFIX, "")
            data = await cache_get_json(key)

            if data:
                # Filter by user if specified
                if user_id and data.get("user_id") != user_id:
                    continue

                sessions.append({
                    "session_id": session_id,
                    "user_id": data.get("user_id"),
                    "created_at": data.get("created_at"),
                    "last_active": data.get("last_active"),
                    "message_count": data.get("message_count", 0),
                    "conversation_type": data.get("conversation_type", "general")
                })

        # Sort by last active (most recent first)
        sessions.sort(key=lambda x: x.get("last_active", ""), reverse=True)
        return sessions

    async def get_session_count(self) -> int:
        """
        Get the total number of active sessions.

        Returns:
            Number of sessions
        """
        cache = self._get_cache()
        keys = await cache.keys(f"{SESSION_KEY_PREFIX}*")
        return len(keys)

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        Note: Redis handles expiration automatically, but this is useful for memory cache.

        Returns:
            Number of sessions cleaned up
        """
        cache = self._get_cache()
        keys = await cache.keys(f"{SESSION_KEY_PREFIX}*")
        cleaned = 0

        cutoff = datetime.utcnow() - timedelta(hours=SESSION_TTL_HOURS)
        cutoff_str = cutoff.isoformat()

        for key in keys:
            data = await cache_get_json(key)
            if data and data.get("last_active", "") < cutoff_str:
                await cache.delete(key)
                cleaned += 1

        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired sessions")

        return cleaned


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
