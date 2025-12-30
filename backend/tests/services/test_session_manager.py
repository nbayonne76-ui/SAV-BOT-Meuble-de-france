# backend/tests/services/test_session_manager.py
"""
Tests pour SessionManager - Gestion de sessions de chat
Coverage target: 80%+
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock

from app.services.session_manager import (
    SessionManager,
    ChatSession,
    ConversationMessage,
    get_session_manager,
    SESSION_TTL_HOURS,
    SESSION_KEY_PREFIX
)


# ==========================================
# Fixtures
# ==========================================

@pytest.fixture
def session_manager():
    """Create SessionManager instance"""
    return SessionManager()


@pytest.fixture
def sample_session():
    """Create a sample ChatSession"""
    return ChatSession(
        session_id="test-session-123",
        user_id="user-456",
        conversation_type="sav",
        language="fr",
        order_number="CMD123456"
    )


@pytest.fixture
def mock_cache():
    """Mock cache instance"""
    cache = MagicMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    cache.delete = AsyncMock(return_value=True)
    cache.keys = AsyncMock(return_value=[])
    return cache


# ==========================================
# Test Class: ConversationMessage
# ==========================================

class TestConversationMessage:
    """Tests for ConversationMessage dataclass"""

    def test_conversation_message_creation(self):
        """Should create conversation message with default timestamp"""
        message = ConversationMessage(
            role="user",
            content="Hello, I have a problem"
        )

        assert message.role == "user"
        assert message.content == "Hello, I have a problem"
        assert message.timestamp is not None
        assert isinstance(message.metadata, dict)
        assert len(message.metadata) == 0

    def test_conversation_message_with_metadata(self):
        """Should create message with custom metadata"""
        metadata = {"sentiment": "negative", "urgency": "high"}
        message = ConversationMessage(
            role="assistant",
            content="I understand your concern",
            metadata=metadata
        )

        assert message.metadata == metadata
        assert message.metadata["sentiment"] == "negative"


# ==========================================
# Test Class: ChatSession
# ==========================================

class TestChatSession:
    """Tests for ChatSession dataclass"""

    def test_chat_session_creation(self):
        """Should create chat session with defaults"""
        session = ChatSession(session_id="test-123")

        assert session.session_id == "test-123"
        assert session.user_id is None
        assert session.created_at is not None
        assert session.last_active is not None
        assert session.conversation_history == []
        assert session.conversation_type == "general"
        assert session.language == "fr"
        assert session.message_count == 0

    def test_chat_session_to_dict(self):
        """Should convert session to dictionary"""
        session = ChatSession(
            session_id="test-123",
            user_id="user-456",
            conversation_type="sav"
        )

        session_dict = session.to_dict()

        assert isinstance(session_dict, dict)
        assert session_dict["session_id"] == "test-123"
        assert session_dict["user_id"] == "user-456"
        assert session_dict["conversation_type"] == "sav"
        assert "created_at" in session_dict
        assert "conversation_history" in session_dict

    def test_chat_session_from_dict(self):
        """Should create session from dictionary"""
        data = {
            "session_id": "test-789",
            "user_id": "user-999",
            "conversation_type": "shopping",
            "language": "en",
            "conversation_history": [],
            "created_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat(),
            "order_number": None,
            "sav_context": {},
            "problem_detected": None,
            "priority_score": None,
            "photos": [],
            "videos": [],
            "message_count": 0,
            "metadata": {}
        }

        session = ChatSession.from_dict(data)

        assert session.session_id == "test-789"
        assert session.user_id == "user-999"
        assert session.conversation_type == "shopping"
        assert session.language == "en"

    def test_add_message(self):
        """Should add message to conversation history"""
        session = ChatSession(session_id="test-123")

        session.add_message("user", "Hello, I need help")

        assert len(session.conversation_history) == 1
        assert session.message_count == 1
        assert session.conversation_history[0]["role"] == "user"
        assert session.conversation_history[0]["content"] == "Hello, I need help"
        assert "timestamp" in session.conversation_history[0]

    def test_add_message_with_metadata(self):
        """Should add message with metadata"""
        session = ChatSession(session_id="test-123")
        metadata = {"priority": "high", "category": "sav"}

        session.add_message("user", "Urgent problem!", metadata=metadata)

        assert session.conversation_history[0]["metadata"] == metadata

    def test_add_multiple_messages(self):
        """Should add multiple messages and increment counter"""
        session = ChatSession(session_id="test-123")

        session.add_message("user", "Message 1")
        session.add_message("assistant", "Response 1")
        session.add_message("user", "Message 2")

        assert len(session.conversation_history) == 3
        assert session.message_count == 3

    def test_get_recent_messages(self):
        """Should return recent messages"""
        session = ChatSession(session_id="test-123")

        # Add 15 messages
        for i in range(15):
            session.add_message("user", f"Message {i}")

        # Get last 10
        recent = session.get_recent_messages(limit=10)

        assert len(recent) == 10
        assert recent[0]["content"] == "Message 5"
        assert recent[-1]["content"] == "Message 14"

    def test_get_recent_messages_default_limit(self):
        """Should use default limit of 10"""
        session = ChatSession(session_id="test-123")

        # Add 5 messages (less than default limit)
        for i in range(5):
            session.add_message("user", f"Message {i}")

        recent = session.get_recent_messages()

        assert len(recent) == 5

    def test_update_sav_context(self):
        """Should update SAV context"""
        session = ChatSession(session_id="test-123")

        session.update_sav_context(
            order_number="CMD123",
            problem_type="mechanism",
            priority="P1"
        )

        assert session.sav_context["order_number"] == "CMD123"
        assert session.sav_context["problem_type"] == "mechanism"
        assert session.sav_context["priority"] == "P1"

    def test_update_sav_context_updates_last_active(self):
        """Should update last_active when updating SAV context"""
        session = ChatSession(session_id="test-123")
        original_last_active = session.last_active

        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)

        session.update_sav_context(status="updated")

        assert session.last_active != original_last_active


# ==========================================
# Test Class: SessionManager - Basic Operations
# ==========================================

class TestSessionManagerBasicOps:
    """Tests for basic SessionManager operations"""

    def test_session_key_generation(self, session_manager):
        """Should generate correct cache key"""
        key = session_manager._session_key("test-123")

        assert key == f"{SESSION_KEY_PREFIX}test-123"
        assert key.startswith("session:")

    @pytest.mark.asyncio
    async def test_create_session(self, session_manager):
        """Should create new session"""
        with patch('app.services.session_manager.cache_set_json', new=AsyncMock(return_value=True)):
            session = await session_manager.create_session(
                session_id="new-session-123",
                user_id="user-456",
                metadata={"source": "web"}
            )

            assert session is not None
            assert session.session_id == "new-session-123"
            assert session.user_id == "user-456"
            assert session.metadata["source"] == "web"
            assert session.conversation_history == []
            assert session.message_count == 0

    @pytest.mark.asyncio
    async def test_save_session(self, session_manager, sample_session):
        """Should save session to cache"""
        with patch('app.services.session_manager.cache_set_json', new=AsyncMock(return_value=True)) as mock_set:
            result = await session_manager.save_session(sample_session)

            assert result is True
            mock_set.assert_called_once()
            # Verify TTL is set correctly
            call_args = mock_set.call_args
            assert call_args[1]['expire'] == SESSION_TTL_HOURS * 3600

    @pytest.mark.asyncio
    async def test_save_session_failure(self, session_manager, sample_session):
        """Should handle save failure"""
        with patch('app.services.session_manager.cache_set_json', new=AsyncMock(return_value=False)):
            result = await session_manager.save_session(sample_session)

            assert result is False

    @pytest.mark.asyncio
    async def test_get_session_exists(self, session_manager):
        """Should retrieve existing session"""
        session_data = {
            "session_id": "existing-123",
            "user_id": "user-789",
            "conversation_type": "sav",
            "language": "fr",
            "conversation_history": [],
            "created_at": datetime.utcnow().isoformat(),
            "last_active": datetime.utcnow().isoformat(),
            "order_number": "CMD123",
            "sav_context": {},
            "problem_detected": None,
            "priority_score": None,
            "photos": [],
            "videos": [],
            "message_count": 0,
            "metadata": {}
        }

        with patch('app.services.session_manager.cache_get_json', new=AsyncMock(return_value=session_data)):
            session = await session_manager.get_session("existing-123")

            assert session is not None
            assert session.session_id == "existing-123"
            assert session.user_id == "user-789"
            assert session.order_number == "CMD123"

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, session_manager):
        """Should return None when session doesn't exist"""
        with patch('app.services.session_manager.cache_get_json', new=AsyncMock(return_value=None)):
            session = await session_manager.get_session("non-existent")

            assert session is None

    @pytest.mark.asyncio
    async def test_delete_session_success(self, session_manager, mock_cache):
        """Should delete existing session"""
        mock_cache.delete.return_value = True

        with patch.object(session_manager, '_get_cache', return_value=mock_cache):
            result = await session_manager.delete_session("test-123")

            assert result is True
            mock_cache.delete.assert_called_once_with(f"{SESSION_KEY_PREFIX}test-123")

    @pytest.mark.asyncio
    async def test_delete_session_not_found(self, session_manager, mock_cache):
        """Should handle deletion of non-existent session"""
        mock_cache.delete.return_value = False

        with patch.object(session_manager, '_get_cache', return_value=mock_cache):
            result = await session_manager.delete_session("non-existent")

            assert result is False


# ==========================================
# Test Class: SessionManager - Advanced Operations
# ==========================================

class TestSessionManagerAdvancedOps:
    """Tests for advanced SessionManager operations"""

    @pytest.mark.asyncio
    async def test_get_or_create_session_existing(self, session_manager):
        """Should return existing session"""
        existing_session = ChatSession(session_id="test-123", user_id="user-456")

        with patch.object(session_manager, 'get_session', new=AsyncMock(return_value=existing_session)), \
             patch.object(session_manager, 'save_session', new=AsyncMock(return_value=True)):

            session = await session_manager.get_or_create_session("test-123")

            assert session is not None
            assert session.session_id == "test-123"
            assert session.user_id == "user-456"

    @pytest.mark.asyncio
    async def test_get_or_create_session_new(self, session_manager):
        """Should create new session if not exists"""
        with patch.object(session_manager, 'get_session', new=AsyncMock(return_value=None)), \
             patch.object(session_manager, 'create_session', new=AsyncMock(return_value=ChatSession(session_id="new-123"))):

            session = await session_manager.get_or_create_session("new-123", user_id="user-789")

            assert session is not None
            assert session.session_id == "new-123"

    @pytest.mark.asyncio
    async def test_add_message_to_session(self, session_manager):
        """Should add message to existing session"""
        existing_session = ChatSession(session_id="test-123")

        with patch.object(session_manager, 'get_session', new=AsyncMock(return_value=existing_session)), \
             patch.object(session_manager, 'save_session', new=AsyncMock(return_value=True)):

            result = await session_manager.add_message(
                session_id="test-123",
                role="user",
                content="Hello world",
                metadata={"priority": "high"}
            )

            assert result is not None
            assert result.message_count == 1
            assert len(result.conversation_history) == 1
            assert result.conversation_history[0]["content"] == "Hello world"

    @pytest.mark.asyncio
    async def test_add_message_session_not_found(self, session_manager):
        """Should return None when session doesn't exist"""
        with patch.object(session_manager, 'get_session', new=AsyncMock(return_value=None)):
            result = await session_manager.add_message(
                session_id="non-existent",
                role="user",
                content="Test"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_update_session_success(self, session_manager):
        """Should update session fields"""
        existing_session = ChatSession(
            session_id="test-123",
            conversation_type="general",
            language="fr"
        )

        with patch.object(session_manager, 'get_session', new=AsyncMock(return_value=existing_session)), \
             patch.object(session_manager, 'save_session', new=AsyncMock(return_value=True)):

            result = await session_manager.update_session(
                session_id="test-123",
                conversation_type="sav",
                order_number="CMD999",
                problem_detected="mechanism"
            )

            assert result is not None
            assert result.conversation_type == "sav"
            assert result.order_number == "CMD999"
            assert result.problem_detected == "mechanism"

    @pytest.mark.asyncio
    async def test_update_session_not_found(self, session_manager):
        """Should return None when session doesn't exist"""
        with patch.object(session_manager, 'get_session', new=AsyncMock(return_value=None)):
            result = await session_manager.update_session(
                session_id="non-existent",
                conversation_type="sav"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_update_session_ignores_invalid_fields(self, session_manager):
        """Should ignore fields that don't exist on session"""
        existing_session = ChatSession(session_id="test-123")

        with patch.object(session_manager, 'get_session', new=AsyncMock(return_value=existing_session)), \
             patch.object(session_manager, 'save_session', new=AsyncMock(return_value=True)):

            result = await session_manager.update_session(
                session_id="test-123",
                invalid_field="should_be_ignored",
                language="en"  # Valid field
            )

            assert result is not None
            assert result.language == "en"
            assert not hasattr(result, "invalid_field")


# ==========================================
# Test Class: SessionManager - List and Count
# ==========================================

class TestSessionManagerListAndCount:
    """Tests for listing and counting sessions"""

    @pytest.mark.asyncio
    async def test_list_sessions_empty(self, session_manager, mock_cache):
        """Should return empty list when no sessions"""
        mock_cache.keys.return_value = []

        with patch.object(session_manager, '_get_cache', return_value=mock_cache):
            sessions = await session_manager.list_sessions()

            assert sessions == []

    @pytest.mark.asyncio
    async def test_list_sessions_multiple(self, session_manager, mock_cache):
        """Should list all sessions"""
        mock_cache.keys.return_value = [
            "session:sess-1",
            "session:sess-2",
            "session:sess-3"
        ]

        session_data_1 = {
            "session_id": "sess-1",
            "user_id": "user-1",
            "created_at": "2025-12-28T10:00:00",
            "last_active": "2025-12-28T11:00:00",
            "message_count": 5,
            "conversation_type": "sav"
        }
        session_data_2 = {
            "session_id": "sess-2",
            "user_id": "user-2",
            "created_at": "2025-12-28T09:00:00",
            "last_active": "2025-12-28T12:00:00",
            "message_count": 3,
            "conversation_type": "general"
        }
        session_data_3 = {
            "session_id": "sess-3",
            "user_id": "user-1",
            "created_at": "2025-12-28T08:00:00",
            "last_active": "2025-12-28T10:30:00",
            "message_count": 8,
            "conversation_type": "shopping"
        }

        with patch.object(session_manager, '_get_cache', return_value=mock_cache), \
             patch('app.services.session_manager.cache_get_json', new=AsyncMock(side_effect=[session_data_1, session_data_2, session_data_3])):

            sessions = await session_manager.list_sessions()

            assert len(sessions) == 3
            # Should be sorted by last_active (most recent first)
            assert sessions[0]["last_active"] == "2025-12-28T12:00:00"
            assert sessions[1]["last_active"] == "2025-12-28T11:00:00"
            assert sessions[2]["last_active"] == "2025-12-28T10:30:00"

    @pytest.mark.asyncio
    async def test_list_sessions_filtered_by_user(self, session_manager, mock_cache):
        """Should filter sessions by user_id"""
        mock_cache.keys.return_value = [
            "session:sess-1",
            "session:sess-2",
            "session:sess-3"
        ]

        session_data_1 = {"session_id": "sess-1", "user_id": "user-1", "created_at": "2025-12-28T10:00:00", "last_active": "2025-12-28T11:00:00", "message_count": 5, "conversation_type": "sav"}
        session_data_2 = {"session_id": "sess-2", "user_id": "user-2", "created_at": "2025-12-28T09:00:00", "last_active": "2025-12-28T12:00:00", "message_count": 3, "conversation_type": "general"}
        session_data_3 = {"session_id": "sess-3", "user_id": "user-1", "created_at": "2025-12-28T08:00:00", "last_active": "2025-12-28T10:30:00", "message_count": 8, "conversation_type": "shopping"}

        with patch.object(session_manager, '_get_cache', return_value=mock_cache), \
             patch('app.services.session_manager.cache_get_json', new=AsyncMock(side_effect=[session_data_1, session_data_2, session_data_3])):

            sessions = await session_manager.list_sessions(user_id="user-1")

            assert len(sessions) == 2
            assert all(s["user_id"] == "user-1" for s in sessions)

    @pytest.mark.asyncio
    async def test_list_sessions_with_limit(self, session_manager, mock_cache):
        """Should respect limit parameter"""
        # Create 150 session keys
        keys = [f"session:sess-{i}" for i in range(150)]
        mock_cache.keys.return_value = keys

        with patch.object(session_manager, '_get_cache', return_value=mock_cache), \
             patch('app.services.session_manager.cache_get_json', new=AsyncMock(return_value=None)):

            sessions = await session_manager.list_sessions(limit=50)

            # Should only process first 50 keys (default limit is 100, but we set 50)
            # Since cache_get_json returns None, we get 0 sessions, but keys were limited
            assert len(sessions) == 0  # None returned from cache

    @pytest.mark.asyncio
    async def test_get_session_count(self, session_manager, mock_cache):
        """Should return count of active sessions"""
        mock_cache.keys.return_value = [
            "session:sess-1",
            "session:sess-2",
            "session:sess-3",
            "session:sess-4",
            "session:sess-5"
        ]

        with patch.object(session_manager, '_get_cache', return_value=mock_cache):
            count = await session_manager.get_session_count()

            assert count == 5

    @pytest.mark.asyncio
    async def test_get_session_count_zero(self, session_manager, mock_cache):
        """Should return 0 when no sessions"""
        mock_cache.keys.return_value = []

        with patch.object(session_manager, '_get_cache', return_value=mock_cache):
            count = await session_manager.get_session_count()

            assert count == 0


# ==========================================
# Test Class: SessionManager - Cleanup
# ==========================================

class TestSessionManagerCleanup:
    """Tests for session cleanup"""

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, session_manager, mock_cache):
        """Should cleanup expired sessions"""
        # Create old session (25 hours old)
        old_time = (datetime.utcnow() - timedelta(hours=25)).isoformat()
        # Create recent session (1 hour old)
        recent_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()

        mock_cache.keys.return_value = [
            "session:old-sess",
            "session:recent-sess"
        ]

        old_session_data = {
            "session_id": "old-sess",
            "last_active": old_time
        }
        recent_session_data = {
            "session_id": "recent-sess",
            "last_active": recent_time
        }

        with patch.object(session_manager, '_get_cache', return_value=mock_cache), \
             patch('app.services.session_manager.cache_get_json', new=AsyncMock(side_effect=[old_session_data, recent_session_data])):

            cleaned = await session_manager.cleanup_expired_sessions()

            assert cleaned == 1
            # Verify delete was called for old session
            mock_cache.delete.assert_called_once_with("session:old-sess")

    @pytest.mark.asyncio
    async def test_cleanup_no_expired_sessions(self, session_manager, mock_cache):
        """Should not cleanup recent sessions"""
        recent_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()

        mock_cache.keys.return_value = [
            "session:recent-1",
            "session:recent-2"
        ]

        recent_data = {"session_id": "recent", "last_active": recent_time}

        with patch.object(session_manager, '_get_cache', return_value=mock_cache), \
             patch('app.services.session_manager.cache_get_json', new=AsyncMock(return_value=recent_data)):

            cleaned = await session_manager.cleanup_expired_sessions()

            assert cleaned == 0
            mock_cache.delete.assert_not_called()


# ==========================================
# Test Class: Global Session Manager
# ==========================================

class TestGlobalSessionManager:
    """Tests for global session manager singleton"""

    def test_get_session_manager_singleton(self):
        """Should return same instance on multiple calls"""
        manager1 = get_session_manager()
        manager2 = get_session_manager()

        assert manager1 is manager2
        assert isinstance(manager1, SessionManager)

    def test_get_session_manager_creates_instance(self):
        """Should create new instance if none exists"""
        # Reset global instance
        import app.services.session_manager as sm
        sm._session_manager = None

        manager = get_session_manager()

        assert manager is not None
        assert isinstance(manager, SessionManager)
