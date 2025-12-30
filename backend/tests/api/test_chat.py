# backend/tests/api/test_chat.py
"""
Comprehensive tests for chat API endpoints.
Tests chat, session management, and ticket creation endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.main import app
from app.api.endpoints.chat import extract_order_number, get_openai_api_key, ChatRequest


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_session_manager():
    """Mock session manager"""
    manager = AsyncMock()

    # Mock session
    mock_session = MagicMock()
    mock_session.session_id = "test-session"
    mock_session.conversation_history = []
    mock_session.conversation_type = "general"
    mock_session.sav_context = {}

    manager.get_or_create_session = AsyncMock(return_value=mock_session)
    manager.update_session = AsyncMock(return_value=mock_session)
    manager.delete_session = AsyncMock(return_value=True)
    manager.get_session_count = AsyncMock(return_value=5)

    return manager


@pytest.fixture
def mock_chatbot():
    """Mock chatbot instance"""
    bot = MagicMock()
    bot.conversation_history = []
    bot.conversation_type = "general"

    # Mock chat response
    async def mock_chat(*args, **kwargs):
        return {
            "response": "Test response",
            "language": "fr",
            "conversation_type": "general"
        }

    bot.chat = AsyncMock(side_effect=mock_chat)
    return bot


# ============================================================================
# TESTS: Utility Functions
# ============================================================================

class TestExtractOrderNumber:
    """Tests for extract_order_number utility function"""

    def test_extract_standard_format(self):
        """Should extract standard CMD-XXXX-XXXXX format"""
        message = "Ma commande CMD-1234-56789 a un problème"
        result = extract_order_number(message)
        assert result == "CMD-1234-56789"

    def test_extract_compact_format(self):
        """Should extract compact CMD-XXXXXXXXXX format"""
        message = "Commande CMD-1234567890 défectueuse"
        result = extract_order_number(message)
        assert result == "CMD-1234567890"

    def test_extract_with_prefix(self):
        """Should extract with 'commande' prefix"""
        message = "commande: CMD-2023-12345"
        result = extract_order_number(message)
        assert result == "CMD-2023-12345"

    def test_extract_no_hyphen(self):
        """Should extract and format CMD without hyphens"""
        message = "CMD1234567890"
        result = extract_order_number(message)
        assert result == "CMD-1234-567890"

    def test_extract_no_match(self):
        """Should return None if no order number found"""
        message = "J'ai un problème avec mon canapé"
        result = extract_order_number(message)
        assert result is None

    def test_extract_case_insensitive(self):
        """Should be case insensitive"""
        message = "cmd-5555-99999"
        result = extract_order_number(message)
        assert result is not None


class TestGetOpenAIAPIKey:
    """Tests for get_openai_api_key dependency"""

    def test_get_key_when_configured(self):
        """Should return key when configured"""
        with patch('app.api.endpoints.chat.settings.OPENAI_API_KEY', 'test-key'):
            result = get_openai_api_key()
            assert result == 'test-key'

    def test_raise_error_when_not_configured(self):
        """Should raise HTTPException when key not configured"""
        from fastapi import HTTPException
        with patch('app.api.endpoints.chat.settings.OPENAI_API_KEY', ''):
            with pytest.raises(HTTPException) as exc_info:
                get_openai_api_key()
            assert exc_info.value.status_code == 500
            assert "not configured" in exc_info.value.detail


# ============================================================================
# TESTS: ChatRequest Validation
# ============================================================================

class TestChatRequestValidation:
    """Tests for ChatRequest Pydantic model validation"""

    def test_valid_message(self):
        """Should accept valid message"""
        request = ChatRequest(message="Hello, how are you?")
        assert request.message == "Hello, how are you?"

    def test_message_sanitization(self):
        """Should sanitize message (trim, remove null bytes, limit newlines)"""
        request = ChatRequest(message="  Test\x00message\n\n\n\ntest  ")
        assert request.message == "Test\x00message\n\ntest".replace('\x00', '')  # Null bytes removed

    def test_empty_message_raises_error(self):
        """Should reject empty message"""
        with pytest.raises(ValueError, match="Message cannot be empty"):
            ChatRequest(message="   ")

    def test_message_too_long(self):
        """Should reject message exceeding max length"""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ChatRequest(message="a" * 5000)  # Max is 4000

    def test_valid_session_id(self):
        """Should accept valid session ID"""
        request = ChatRequest(message="test", session_id="my-session-123")
        assert request.session_id == "my-session-123"

    def test_invalid_session_id_format(self):
        """Should reject invalid session ID format"""
        with pytest.raises(ValueError, match="Invalid session ID format"):
            ChatRequest(message="test", session_id="invalid@session!")

    def test_valid_order_number(self):
        """Should accept and format valid order number"""
        request = ChatRequest(message="test", order_number="CMD-1234-56789")
        assert request.order_number == "CMD-1234-56789"

    def test_invalid_order_number_format(self):
        """Should reject invalid order number"""
        with pytest.raises(ValueError, match="Invalid order number format"):
            ChatRequest(message="test", order_number="INVALID-123")

    def test_photos_limit(self):
        """Should reject more than 10 photos"""
        with pytest.raises(ValueError, match="Maximum 10 photos"):
            ChatRequest(message="test", photos=["photo" + str(i) for i in range(11)])


# ============================================================================
# TESTS: POST /chat Endpoint
# ============================================================================

class TestChatEndpoint:
    """Tests for main chat endpoint"""

    def test_chat_success_basic(self, client, mock_session_manager, mock_chatbot):
        """Should successfully process chat message"""
        with patch('app.api.endpoints.chat.get_session_manager', return_value=mock_session_manager), \
             patch('app.api.endpoints.chat.MeubledeFranceChatbot', return_value=mock_chatbot), \
             patch('app.api.endpoints.chat.settings.OPENAI_API_KEY', 'test-key'):

            response = client.post("/api/chat", json={
                "message": "Bonjour, j'ai un problème",
                "session_id": "test-session"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Test response"
            assert data["language"] == "fr"
            assert data["conversation_type"] == "general"
            assert data["session_id"] == "test-session"

    def test_chat_with_order_number(self, client, mock_session_manager, mock_chatbot):
        """Should handle order number in request"""
        with patch('app.api.endpoints.chat.get_session_manager', return_value=mock_session_manager), \
             patch('app.api.endpoints.chat.MeubledeFranceChatbot', return_value=mock_chatbot), \
             patch('app.api.endpoints.chat.settings.OPENAI_API_KEY', 'test-key'):

            response = client.post("/api/chat", json={
                "message": "J'ai un problème",
                "session_id": "test",
                "order_number": "CMD-1234-56789"
            })

            assert response.status_code == 200
            # Verify chatbot.chat was called with order_number
            mock_chatbot.chat.assert_called_once()
            call_kwargs = mock_chatbot.chat.call_args[1]
            assert call_kwargs["order_number"] == "CMD-1234-56789"

    def test_chat_auto_detects_order_number(self, client, mock_session_manager, mock_chatbot):
        """Should auto-detect order number from message"""
        with patch('app.api.endpoints.chat.get_session_manager', return_value=mock_session_manager), \
             patch('app.api.endpoints.chat.MeubledeFranceChatbot', return_value=mock_chatbot), \
             patch('app.api.endpoints.chat.settings.OPENAI_API_KEY', 'test-key'):

            response = client.post("/api/chat", json={
                "message": "Ma commande CMD-9999-88888 est défectueuse",
                "session_id": "test"
            })

            assert response.status_code == 200
            # Verify auto-detected order number was passed
            call_kwargs = mock_chatbot.chat.call_args[1]
            assert call_kwargs["order_number"] == "CMD-9999-88888"

    def test_chat_handles_photos(self, client, mock_session_manager, mock_chatbot):
        """Should handle photos in request"""
        with patch('app.api.endpoints.chat.get_session_manager', return_value=mock_session_manager), \
             patch('app.api.endpoints.chat.MeubledeFranceChatbot', return_value=mock_chatbot), \
             patch('app.api.endpoints.chat.settings.OPENAI_API_KEY', 'test-key'):

            response = client.post("/api/chat", json={
                "message": "Voici les photos",
                "session_id": "test",
                "photos": ["/uploads/photo1.jpg", "/uploads/photo2.jpg"]
            })

            assert response.status_code == 200
            call_kwargs = mock_chatbot.chat.call_args[1]
            assert call_kwargs["photos"] == ["/uploads/photo1.jpg", "/uploads/photo2.jpg"]

    def test_chat_handles_sav_ticket_response(self, client, mock_session_manager, mock_chatbot):
        """Should return SAV ticket when created"""
        mock_chatbot.chat = AsyncMock(return_value={
            "response": "Ticket créé",
            "language": "fr",
            "conversation_type": "sav",
            "sav_ticket": {"ticket_id": "SAV-001", "priority": "P1"}
        })

        with patch('app.api.endpoints.chat.get_session_manager', return_value=mock_session_manager), \
             patch('app.api.endpoints.chat.MeubledeFranceChatbot', return_value=mock_chatbot), \
             patch('app.api.endpoints.chat.settings.OPENAI_API_KEY', 'test-key'):

            response = client.post("/api/chat", json={
                "message": "Mon canapé est cassé",
                "session_id": "test",
                "order_number": "CMD-1111-22222"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["sav_ticket"] is not None
            assert data["sav_ticket"]["ticket_id"] == "SAV-001"

    def test_chat_invalid_message(self, client):
        """Should reject invalid message"""
        response = client.post("/api/chat", json={
            "message": "",
            "session_id": "test"
        })

        assert response.status_code == 422  # Validation error

    def test_chat_missing_api_key(self, client, mock_session_manager, mock_chatbot):
        """Should return 500 when API key missing"""
        with patch('app.api.endpoints.chat.settings.OPENAI_API_KEY', ''):
            response = client.post("/api/chat", json={
                "message": "Test",
                "session_id": "test"
            })

            assert response.status_code == 500

    def test_chat_session_management(self, client, mock_session_manager, mock_chatbot):
        """Should create/update session"""
        with patch('app.api.endpoints.chat.get_session_manager', return_value=mock_session_manager), \
             patch('app.api.endpoints.chat.MeubledeFranceChatbot', return_value=mock_chatbot), \
             patch('app.api.endpoints.chat.settings.OPENAI_API_KEY', 'test-key'):

            response = client.post("/api/chat", json={
                "message": "Test message",
                "session_id": "new-session"
            })

            assert response.status_code == 200
            # Verify session was created
            mock_session_manager.get_or_create_session.assert_called_once()
            # Verify session was updated
            mock_session_manager.update_session.assert_called_once()


# ============================================================================
# TESTS: DELETE /chat/{session_id} Endpoint
# ============================================================================

class TestClearSessionEndpoint:
    """Tests for clear session endpoint"""

    def test_clear_session_success(self, client, mock_session_manager):
        """Should successfully clear session"""
        with patch('app.api.endpoints.chat.get_session_manager', return_value=mock_session_manager):
            response = client.delete("/api/chat/test-session-123")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "cleared" in data["message"].lower()
            mock_session_manager.delete_session.assert_called_once_with("test-session-123")

    def test_clear_session_not_found(self, client, mock_session_manager):
        """Should return success=False when session not found"""
        mock_session_manager.delete_session = AsyncMock(return_value=False)

        with patch('app.api.endpoints.chat.get_session_manager', return_value=mock_session_manager):
            response = client.delete("/api/chat/nonexistent")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "not found" in data["message"].lower()

    def test_clear_session_invalid_id_format(self, client):
        """Should reject invalid session ID format"""
        response = client.delete("/api/chat/invalid@session!")

        assert response.status_code == 400
        assert "Invalid session ID format" in response.json()["detail"]


# ============================================================================
# TESTS: GET /chat/sessions/count Endpoint
# ============================================================================

class TestSessionCountEndpoint:
    """Tests for session count endpoint"""

    def test_get_session_count(self, client, mock_session_manager):
        """Should return session count"""
        with patch('app.api.endpoints.chat.get_session_manager', return_value=mock_session_manager), \
             patch('app.api.endpoints.chat.settings.REDIS_URL', 'redis://localhost'):

            response = client.get("/api/chat/sessions/count")

            assert response.status_code == 200
            data = response.json()
            assert data["active_sessions"] == 5
            assert data["storage_backend"] == "redis"

    def test_get_session_count_memory_backend(self, client, mock_session_manager):
        """Should indicate memory backend when not using Redis"""
        with patch('app.api.endpoints.chat.get_session_manager', return_value=mock_session_manager), \
             patch('app.api.endpoints.chat.settings.REDIS_URL', ''):

            response = client.get("/api/chat/sessions/count")

            assert response.status_code == 200
            data = response.json()
            assert data["storage_backend"] == "memory"


# ============================================================================
# TESTS: POST /chat/create-ticket Endpoint
# ============================================================================

class TestCreateTicketFromChatEndpoint:
    """Tests for creating ticket from text chat"""

    def test_create_ticket_success(self, client):
        """Should create ticket from chat"""
        with patch('app.api.endpoints.chat.warranty_service') as mock_ws, \
             patch('app.api.endpoints.chat.sav_workflow_engine') as mock_sav:

            # Mock warranty creation
            mock_warranty = MagicMock()
            mock_ws.create_warranty = AsyncMock(return_value=mock_warranty)

            # Mock ticket creation
            mock_ticket = MagicMock()
            mock_ticket.ticket_id = "SAV-CHAT-001"
            mock_ticket.priority = "P2"
            mock_ticket.status = "open"
            mock_sav.process_new_claim = AsyncMock(return_value=mock_ticket)

            response = client.post("/api/chat/create-ticket", json={
                "customer_name": "Jean Dupont",
                "problem_description": "Problème avec le canapé",
                "product": "Canapé OSLO",
                "order_number": "CMD-1234-56789"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["ticket_id"] == "SAV-CHAT-001"
            assert data["data"]["customer_name"] == "Jean Dupont"
            assert data["data"]["source"] == "text_chat"

    def test_create_ticket_without_order_number(self, client):
        """Should create ticket even without order number"""
        with patch('app.api.endpoints.chat.warranty_service') as mock_ws, \
             patch('app.api.endpoints.chat.sav_workflow_engine') as mock_sav:

            mock_ws.create_warranty = AsyncMock(return_value=MagicMock())

            mock_ticket = MagicMock()
            mock_ticket.ticket_id = "SAV-CHAT-002"
            mock_ticket.priority = "P3"
            mock_ticket.status = "open"
            mock_sav.process_new_claim = AsyncMock(return_value=mock_ticket)

            response = client.post("/api/chat/create-ticket", json={
                "customer_name": "Marie Martin",
                "problem_description": "Question sur le produit",
                "product": "Table NORDIC"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            # Order number should be generated
            assert data["data"]["order_number"] is not None

    def test_create_ticket_error_handling(self, client):
        """Should handle errors during ticket creation"""
        with patch('app.api.endpoints.chat.warranty_service') as mock_ws:
            mock_ws.create_warranty = AsyncMock(side_effect=Exception("Database error"))

            response = client.post("/api/chat/create-ticket", json={
                "customer_name": "Test User",
                "problem_description": "Test problem",
                "product": "Test Product"
            })

            assert response.status_code == 500
            assert "Erreur" in response.json()["detail"]
