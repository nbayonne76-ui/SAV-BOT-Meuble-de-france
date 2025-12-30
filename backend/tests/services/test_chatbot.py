# backend/tests/services/test_chatbot.py
"""
Comprehensive tests for MeubledeFranceChatbot class
Target: Increase coverage from 12% to 80%+
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from typing import List, Dict

from app.services.chatbot import MeubledeFranceChatbot
from app.core.constants import (
    OPENAI_MODEL,
    OPENAI_MAX_TOKENS,
    OPENAI_TEMPERATURE,
    CONVERSATION_HISTORY_LIMIT
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def chatbot():
    """Create a chatbot instance for testing"""
    return MeubledeFranceChatbot(api_key="sk-test-key-123", timeout=30)


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Bonjour! Comment puis-je vous aider?"
    return mock_response


# ============================================================================
# TESTS: Language Detection
# ============================================================================

class TestLanguageDetection:
    """Tests for language detection functionality"""

    def test_detect_language_french(self, chatbot):
        """Should detect French language"""
        messages = [
            "Bonjour, j'ai un problème",
            "Je voudrais commander",
            "Merci beaucoup",
        ]
        for message in messages:
            assert chatbot.detect_language(message) == "fr"

    def test_detect_language_english(self, chatbot):
        """Should detect English language based on keywords"""
        messages = [
            "Hello, I have a problem",  # 'hello' and 'problem' are EN keywords
            "I need a new sofa",  # 'sofa' is an EN keyword
            "What is your furniture selection?",  # 'furniture' is an EN keyword
        ]
        for message in messages:
            assert chatbot.detect_language(message) == "en"

    def test_detect_language_default_french(self, chatbot):
        """Should default to French for ambiguous text"""
        message = "123456"
        assert chatbot.detect_language(message) == "fr"


# ============================================================================
# TESTS: Product Detection
# ============================================================================

class TestProductDetection:
    """Tests for product mention detection"""

    def test_detect_product_mention_disabled(self, chatbot):
        """Should return None as product detection is currently disabled"""
        messages = [
            "Mon canapé est cassé",
            "J'ai un problème avec mon sofa",
            "Le canapé d'angle ne fonctionne pas",
            "Mon fauteuil relax est bloqué",
            "Bonjour, comment allez-vous?",
        ]
        # Product detection is disabled until real catalog is imported
        for message in messages:
            result = chatbot.detect_product_mention(message)
            assert result is None


# ============================================================================
# TESTS: Conversation Type Detection
# ============================================================================

class TestConversationTypeDetection:
    """Tests for conversation type detection"""

    def test_detect_conversation_type_sav(self, chatbot):
        """Should detect SAV conversation based on keywords"""
        messages = [
            "J'ai un problème avec ma commande",  # 'problème' and 'commande' are SAV keywords
            "Il y a un défaut sur le produit",  # 'défaut' is SAV keyword
            "Le produit est cassé",  # 'cassé' is SAV keyword
            "Problème de livraison",  # 'problème' and 'livraison' are SAV keywords
            "Je veux faire une réclamation",  # 'réclamation' is SAV keyword
        ]
        for message in messages:
            result = chatbot.detect_conversation_type(message)
            assert result == "sav"

    def test_detect_conversation_type_shopping(self, chatbot):
        """Should detect shopping conversation based on keywords"""
        messages = [
            "Je voudrais acheter un canapé",  # 'acheter' and 'canapé' are shopping keywords
            "Je cherche un meuble",  # 'cherche' and 'meuble' are shopping keywords
            "J'ai besoin d'une table",  # 'besoin' and 'table' are shopping keywords
        ]
        for message in messages:
            result = chatbot.detect_conversation_type(message)
            assert result == "shopping"

    def test_detect_conversation_type_general(self, chatbot):
        """Should detect general conversation"""
        message = "Bonjour, comment ça va?"
        result = chatbot.detect_conversation_type(message)
        assert result == "general"


# ============================================================================
# TESTS: Priority Classification
# ============================================================================

class TestPriorityClassification:
    """Tests for priority classification"""

    def test_classify_priority_critical(self, chatbot):
        """Should classify as P0 for critical keywords"""
        message = "Le canapé est cassé et c'est dangereux"
        result = chatbot.classify_priority(message)
        assert result["code"] == "P0"
        assert result["label"] == "CRITIQUE"
        assert result["emoji"] == "🔴"
        assert result["requires_escalation"] is True

    def test_classify_priority_high(self, chatbot):
        """Should classify as P1 for high priority keywords"""
        message = "Il y a une déchirure importante sur le canapé"
        result = chatbot.classify_priority(message)
        assert result["code"] == "P1"
        assert result["label"] == "HAUTE"
        assert result["emoji"] == "🟠"

    def test_classify_priority_medium(self, chatbot):
        """Should classify as P2 for medium priority"""
        message = "Il y a un petit défaut mineur sur le côté"
        result = chatbot.classify_priority(message)
        assert result["code"] == "P2"
        assert result["label"] == "MOYENNE"
        assert result["emoji"] == "🟡"

    def test_classify_priority_low(self, chatbot):
        """Should classify as P3 for low/default priority"""
        message = "J'ai une question sur l'entretien du canapé"
        result = chatbot.classify_priority(message)
        assert result["code"] == "P3"
        assert result["label"] == "BASSE"
        assert result["emoji"] == "🟢"


# ============================================================================
# TESTS: Ticket ID Generation
# ============================================================================

class TestTicketIDGeneration:
    """Tests for ticket ID generation"""

    def test_generate_ticket_id_format(self, chatbot):
        """Should generate ticket ID in correct format"""
        ticket_id = chatbot.generate_ticket_id()
        assert ticket_id.startswith("SAV-MDF-")
        # Format: SAV-MDF-YYYYMMDDHHMMSS (total length: 8 + 14 = 22+)
        assert len(ticket_id) >= 22

    def test_generate_ticket_id_unique(self, chatbot):
        """Should generate unique ticket IDs (timestamp-based)"""
        import time
        ids = []
        for _ in range(5):
            ids.append(chatbot.generate_ticket_id())
            time.sleep(1)  # 1 second delay to ensure different timestamps
        # All should be unique due to timestamp
        assert len(set(ids)) == 5


# ============================================================================
# TESTS: User Intent Detection
# ============================================================================

class TestUserIntentDetection:
    """Tests for user intent detection methods"""

    def test_is_user_confirming(self, chatbot):
        """Should detect confirmation messages using constants"""
        confirmations = [
            "Oui",
            "OK",
            "D'accord",
            "valider",  # From CONFIRMATION_KEYWORDS
            "Exactement",
            "confirmer",  # From CONFIRMATION_KEYWORDS
        ]
        for message in confirmations:
            assert chatbot.is_user_confirming(message) is True

    def test_is_user_rejecting(self, chatbot):
        """Should detect rejection messages using constants"""
        rejections = [
            "Non",
            "Pas exactement",
            "Incorrect",
            "Annuler",
        ]
        for message in rejections:
            assert chatbot.is_user_rejecting(message) is True

    def test_is_user_wanting_to_continue(self, chatbot):
        """Should detect continue intent using constants"""
        messages = [
            "Oui, je veux continuer",
            "Autre chose",
            "Encore",
            "J'ai besoin",
        ]
        for message in messages:
            assert chatbot.is_user_wanting_to_continue(message) is True

    def test_is_user_wanting_to_close(self, chatbot):
        """Should detect close intent using constants"""
        messages = [
            "Clôturer",
            "Terminer",
            "Au revoir",
            "Fermer",
        ]
        for message in messages:
            assert chatbot.is_user_wanting_to_close(message) is True


# ============================================================================
# TESTS: System Prompt Creation
# ============================================================================

class TestSystemPromptCreation:
    """Tests for system prompt generation"""

    def test_create_system_prompt_french(self, chatbot):
        """Should create French system prompt"""
        prompt = chatbot.create_system_prompt(language="fr")
        assert len(prompt) > 100  # Substantial prompt
        # Should mention company or role
        assert "mobilier" in prompt.lower() or "france" in prompt.lower() or "assistant" in prompt.lower()

    def test_create_system_prompt_english(self, chatbot):
        """Should create English system prompt"""
        prompt = chatbot.create_system_prompt(language="en")
        assert len(prompt) > 100  # Substantial prompt
        # Should have English content or at least mention the company
        assert "mobilier" in prompt.lower() or "furniture" in prompt.lower() or "assistant" in prompt.lower()

    def test_create_system_prompt_contains_instructions(self, chatbot):
        """Should contain instructions for the AI"""
        prompt = chatbot.create_system_prompt()
        assert len(prompt) > 50  # Should have meaningful content
        # System prompts typically contain role or instructions
        assert prompt  # Not empty


# ============================================================================
# TESTS: Chat Method (Integration)
# ============================================================================

class TestChatMethod:
    """Integration tests for the chat method"""

    @pytest.mark.asyncio
    async def test_chat_general_conversation(self, chatbot, mock_openai_response):
        """Should handle general conversation"""
        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            result = await chatbot.chat("Bonjour, comment ça va?")

            assert "response" in result
            assert result["language"] == "fr"
            assert result["conversation_type"] == "general"
            assert len(chatbot.conversation_history) == 2  # User + assistant

    @pytest.mark.asyncio
    async def test_chat_with_order_number(self, chatbot, mock_openai_response):
        """Should fetch order data when order number provided"""
        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            with patch.object(chatbot, 'fetch_order_data', new=AsyncMock(return_value={"order_id": "12345"})):
                result = await chatbot.chat(
                    "J'ai un problème",
                    order_number="12345"
                )

                assert result is not None
                assert chatbot.client_data == {"order_id": "12345"}

    @pytest.mark.asyncio
    async def test_chat_conversation_history_stored(self, chatbot, mock_openai_response):
        """Should store conversation history"""
        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            # Send multiple messages
            for i in range(3):
                await chatbot.chat(f"Message {i}")

            # Should have stored messages (user + assistant for each)
            assert len(chatbot.conversation_history) == 6  # 3 exchanges * 2 messages

    @pytest.mark.asyncio
    async def test_chat_uses_correct_openai_config(self, chatbot, mock_openai_response):
        """Should use constants for OpenAI configuration"""
        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)) as mock_create:
            await chatbot.chat("Test message")

            # Verify OpenAI was called with correct config
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["model"] == OPENAI_MODEL
            assert call_kwargs["max_tokens"] == OPENAI_MAX_TOKENS
            assert call_kwargs["temperature"] == OPENAI_TEMPERATURE

    @pytest.mark.asyncio
    async def test_chat_error_handling(self, chatbot):
        """Should handle OpenAI API errors gracefully"""
        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(side_effect=Exception("API Error"))):
            result = await chatbot.chat("Test message")

            # Should return error response
            assert "error" in result or "response" in result


# ============================================================================
# TESTS: Photo Handling
# ============================================================================

class TestPhotoHandling:
    """Tests for photo upload and handling"""

    @pytest.mark.asyncio
    async def test_chat_with_photo_upload(self, chatbot, mock_openai_response):
        """Should handle photo uploads"""
        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            photos = ["http://example.com/photo1.jpg", "http://example.com/photo2.jpg"]
            result = await chatbot.chat(
                "Voici les photos du problème",
                photos=photos
            )

            assert len(chatbot.pending_photos) == 2
            assert result is not None

    @pytest.mark.asyncio
    async def test_awaiting_photos_reminder(self, chatbot, mock_openai_response):
        """Should remind user to upload photos when awaiting"""
        chatbot.awaiting_photos = True

        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            result = await chatbot.chat("Un autre message sans photos")

            # Should get photo reminder
            assert "photo" in result["response"].lower() or "📸" in result["response"]


# ============================================================================
# TESTS: Reset Conversation
# ============================================================================

class TestResetConversation:
    """Tests for conversation reset"""

    def test_reset_conversation(self, chatbot):
        """Should reset all conversation state"""
        # Setup state
        chatbot.conversation_history = [{"role": "user", "content": "test"}]
        chatbot.client_data = {"test": "data"}
        chatbot.conversation_type = "sav"
        chatbot.pending_photos = ["photo.jpg"]
        chatbot.awaiting_confirmation = True

        # Reset
        chatbot.reset_conversation()

        # Verify reset
        assert len(chatbot.conversation_history) == 0
        assert chatbot.client_data == {}
        assert chatbot.conversation_type == "general"
        assert len(chatbot.pending_photos) == 0
        assert chatbot.awaiting_confirmation is False


# ============================================================================
# TESTS: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error conditions"""

    @pytest.mark.asyncio
    async def test_chat_empty_message(self, chatbot, mock_openai_response):
        """Should handle empty messages"""
        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            result = await chatbot.chat("")
            assert result is not None

    @pytest.mark.asyncio
    async def test_chat_very_long_message(self, chatbot, mock_openai_response):
        """Should handle very long messages"""
        long_message = "test " * 1000
        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            result = await chatbot.chat(long_message)
            assert result is not None

    def test_chatbot_initialization(self):
        """Should initialize chatbot correctly"""
        bot = MeubledeFranceChatbot(api_key="test-key", timeout=60)
        assert bot.client is not None
        assert bot.conversation_history == []
        assert bot.conversation_type == "general"

    def test_detect_language_special_characters(self, chatbot):
        """Should handle special characters in language detection"""
        message = "Héllo! Çà va? 🎉"
        result = chatbot.detect_language(message)
        assert result in ["fr", "en"]


# ============================================================================
# TESTS: SAV Workflow Methods
# ============================================================================

class TestOrderDataFetching:
    """Tests for order data fetching"""

    @pytest.mark.asyncio
    async def test_fetch_order_data_success(self, chatbot):
        """Should fetch order data successfully"""
        order_number = "CMD123456"
        result = await chatbot.fetch_order_data(order_number)

        # Verify structure
        assert result is not None
        assert "order_number" in result
        assert result["order_number"] == order_number
        assert "name" in result
        assert "email" in result
        assert "product" in result
        assert "delivery_date" in result
        assert "amount" in result
        assert "warranty_status" in result

    @pytest.mark.asyncio
    async def test_fetch_order_data_returns_mock_data(self, chatbot):
        """Should return mock data with expected values"""
        result = await chatbot.fetch_order_data("TEST123")

        # Verify mock data structure
        assert result["name"] == "Client Example"
        assert result["email"] == "client@example.fr"
        assert result["phone"] == "+33612345678"
        assert isinstance(result["amount"], float)
        assert result["amount"] > 0


class TestTicketValidationPreparation:
    """Tests for ticket validation preparation (without creating ticket)"""

    @pytest.mark.asyncio
    async def test_prepare_ticket_validation_complete(self, chatbot):
        """Should prepare ticket validation with all required data"""
        user_message = "Mon canapé a un problème de mécanisme, il ne se déplie plus"
        order_number = "CMD123456"

        # Mock dependencies - patch the actual service modules
        with patch('app.services.warranty_service.warranty_service') as mock_ws, \
             patch('app.services.problem_detector.problem_detector') as mock_pd, \
             patch('app.services.priority_scorer.priority_scorer') as mock_ps:

            # Setup mocks
            mock_warranty = MagicMock()
            mock_ws.create_warranty = AsyncMock(return_value=mock_warranty)

            mock_problem_result = MagicMock()
            mock_problem_result.primary_category = "mechanism"
            mock_problem_result.severity = "P1"
            mock_problem_result.confidence = 0.85
            mock_pd.detect_problem_type.return_value = mock_problem_result

            mock_warranty_check = MagicMock()
            mock_warranty_check.is_covered = True
            mock_warranty_check.component = "Mécanisme de dépliage"
            mock_ws.check_warranty_coverage.return_value = mock_warranty_check

            mock_priority_result = MagicMock()
            mock_priority_result.priority = "P1"
            mock_priority_result.total_score = 75
            mock_priority_result.explanation = "Haute priorité"
            mock_ps.calculate_priority.return_value = mock_priority_result

            # Execute
            result = await chatbot.prepare_ticket_validation(user_message, order_number)

            # Verify
            assert result is not None
            assert chatbot.pending_ticket_validation is not None
            assert chatbot.pending_ticket_validation["order_number"] == order_number
            assert chatbot.pending_ticket_validation["problem_description"] == user_message
            assert chatbot.pending_ticket_validation["priority"] == "P1"
            assert chatbot.pending_ticket_validation["warranty_covered"] is True

    @pytest.mark.asyncio
    async def test_prepare_ticket_validation_sets_awaiting_photos(self, chatbot):
        """Should set awaiting_photos flag after preparation"""
        user_message = "Problème de tissu déchiré sur mon fauteuil"
        order_number = "CMD789"

        # Mock dependencies - patch the actual service modules
        with patch('app.services.warranty_service.warranty_service') as mock_ws, \
             patch('app.services.problem_detector.problem_detector') as mock_pd, \
             patch('app.services.priority_scorer.priority_scorer') as mock_ps:

            mock_ws.create_warranty = AsyncMock(return_value=MagicMock())

            mock_problem = MagicMock()
            mock_problem.primary_category = "fabric"
            mock_problem.severity = "P2"
            mock_problem.confidence = 0.9
            mock_pd.detect_problem_type.return_value = mock_problem

            mock_warranty = MagicMock()
            mock_warranty.is_covered = True
            mock_warranty.component = "Tissu"
            mock_ws.check_warranty_coverage.return_value = mock_warranty

            mock_priority = MagicMock()
            mock_priority.priority = "P2"
            mock_priority.total_score = 45
            mock_priority.explanation = "Priorité moyenne"
            mock_ps.calculate_priority.return_value = mock_priority

            await chatbot.prepare_ticket_validation(user_message, order_number)

            # Verify flags are set correctly
            assert chatbot.awaiting_photos is True
            assert chatbot.awaiting_confirmation is False


class TestValidationSummaryGeneration:
    """Tests for validation summary generation with photos"""

    def test_generate_validation_summary_formatting(self, chatbot):
        """Should generate properly formatted summary"""
        # Setup pending validation data
        chatbot.pending_ticket_validation = {
            "order_number": "CMD123456",
            "customer_name": "Jean Dupont",
            "product_name": "Canapé OSLO 3 places",
            "problem_description": "Problème de mécanisme",
            "warranty_covered": True,
            "warranty_component": "Mécanisme",
            "priority": "P1",
            "priority_explanation": "Haute priorité - mécanisme défectueux"
        }
        chatbot.pending_photos = []

        # Generate summary
        summary = chatbot.generate_validation_summary_with_photos()

        # Verify formatting
        assert summary is not None
        assert "RÉCAPITULATIF" in summary
        assert "CMD123456" in summary
        assert "Jean Dupont" in summary
        assert "Canapé OSLO 3 places" in summary
        assert "Problème de mécanisme" in summary
        assert "✅ Couvert" in summary
        assert "P1" in summary
        assert "OUI" in summary  # Validation prompt
        assert "NON" in summary  # Rejection prompt

    def test_generate_validation_summary_with_photos_list(self, chatbot):
        """Should include photo list when photos are present"""
        chatbot.pending_ticket_validation = {
            "order_number": "CMD999",
            "customer_name": "Marie Martin",
            "product_name": "Fauteuil RELAX",
            "problem_description": "Tache sur le tissu",
            "warranty_covered": False,
            "warranty_component": "N/A",
            "priority": "P3",
            "priority_explanation": "Basse priorité"
        }
        chatbot.pending_photos = [
            "/uploads/photo1.jpg",
            "/uploads/photo2.jpg",
            "/uploads/photo3.jpg"
        ]

        summary = chatbot.generate_validation_summary_with_photos()

        # Verify photos section
        assert "3 photo(s)" in summary
        assert "Liste des photos" in summary
        assert "photo1.jpg" in summary
        assert "photo2.jpg" in summary
        assert "photo3.jpg" in summary

    def test_generate_validation_summary_no_pending_ticket(self, chatbot):
        """Should return empty string if no pending ticket"""
        chatbot.pending_ticket_validation = None

        summary = chatbot.generate_validation_summary_with_photos()

        assert summary == ""


class TestTicketCreationAfterValidation:
    """Tests for ticket creation after user validation"""

    @pytest.mark.asyncio
    async def test_create_ticket_after_validation_success(self, chatbot):
        """Should create ticket after validation using pending data"""
        # Create proper warranty mock with required attributes
        mock_warranty = MagicMock()
        mock_warranty.warranty_id = "WARRANTY-12345"
        mock_warranty.product_sku = "OSLO-3P-GREY"
        mock_warranty.customer_id = "client@example.fr"

        # Setup pending validation
        chatbot.pending_ticket_validation = {
            "customer_id": "client@example.fr",
            "order_number": "CMD123456",
            "product_sku": "OSLO-3P-GREY",
            "product_name": "Canapé OSLO 3 places",
            "problem_description": "Mécanisme bloqué",
            "warranty": mock_warranty,
            "product_value": 1890.0
        }
        chatbot.client_data = {"amount": 1890.0}

        # Mock sav_workflow_engine - patch the import in chatbot module
        with patch('app.services.chatbot.sav_workflow_engine') as mock_sav, \
             patch('app.services.chatbot.evidence_collector') as mock_ec:

            # Create complete mock ticket with all required attributes
            from datetime import datetime
            mock_ticket = MagicMock()
            mock_ticket.ticket_id = "SAV-20251228-CMD123456"
            mock_ticket.status = "open"
            mock_ticket.priority = "P1"
            mock_ticket.problem_category = "mechanism"
            mock_ticket.problem_severity = "P1"
            mock_ticket.warranty_check_result = MagicMock()
            mock_ticket.warranty_check_result.is_covered = True
            mock_ticket.auto_resolved = False
            mock_ticket.resolution_type = None
            mock_ticket.resolution_description = None
            mock_ticket.created_at = datetime.now()
            mock_sav.process_new_claim = AsyncMock(return_value=mock_ticket)

            mock_ec.generate_evidence_request_message.return_value = "Veuillez fournir des photos"

            # Execute
            result = await chatbot.create_ticket_after_validation()

            # Verify - result is a dict (self.ticket_data), not the ticket object
            assert result is not None
            assert isinstance(result, dict)
            assert result["ticket_id"] == "SAV-20251228-CMD123456"  # From mock_ticket.ticket_id
            assert result["priority"]["code"] == "P1"
            assert result["problem_category"] == "mechanism"
            mock_sav.process_new_claim.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_ticket_after_validation_raises_if_no_pending(self, chatbot):
        """Should raise ValueError if no pending validation"""
        chatbot.pending_ticket_validation = None

        # Should raise ValueError
        with pytest.raises(ValueError, match="Aucun ticket en attente de validation"):
            await chatbot.create_ticket_after_validation()


class TestSavWorkflowHandler:
    """Tests for SAV workflow handler"""

    @pytest.mark.asyncio
    async def test_handle_sav_workflow_no_order_number(self, chatbot):
        """Should return None if no order number provided"""
        result = await chatbot.handle_sav_workflow(
            user_message="Mon canapé est défectueux",
            order_number=None
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_sav_workflow_wrong_conversation_type(self, chatbot):
        """Should return None if conversation type is not SAV"""
        chatbot.conversation_type = "shopping"  # Not SAV

        result = await chatbot.handle_sav_workflow(
            user_message="Mon canapé est défectueux",
            order_number="CMD123"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_sav_workflow_message_too_short(self, chatbot):
        """Should return None if message is too short (< 20 chars)"""
        chatbot.conversation_type = "sav"

        result = await chatbot.handle_sav_workflow(
            user_message="Court",  # Only 5 chars
            order_number="CMD123"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_handle_sav_workflow_success(self, chatbot):
        """Should successfully initiate SAV workflow when conditions are met"""
        chatbot.conversation_type = "sav"
        user_message = "Mon canapé OSLO a un problème de mécanisme qui ne se déplie plus correctement"
        order_number = "CMD123456"

        # Mock all dependencies - patch imports in chatbot module
        with patch('app.services.chatbot.warranty_service') as mock_ws, \
             patch('app.services.chatbot.sav_workflow_engine') as mock_sav, \
             patch('app.services.chatbot.evidence_collector') as mock_ec:

            mock_warranty = MagicMock()
            mock_ws.create_warranty = AsyncMock(return_value=mock_warranty)

            mock_ticket = MagicMock()
            mock_ticket.id = "SAV-MDF-20251228123456"
            mock_ticket.problem_category = "mechanism"
            mock_ticket.priority = "P1"
            mock_sav.process_new_claim = AsyncMock(return_value=mock_ticket)

            mock_ec.generate_evidence_request_message.return_value = "Photos requises"

            # Execute
            result = await chatbot.handle_sav_workflow(user_message, order_number)

            # Verify workflow was initiated
            assert result is not None
            mock_ws.create_warranty.assert_called_once()
            mock_sav.process_new_claim.assert_called_once()


class TestSavWorkflowIntegration:
    """Tests for complete SAV workflow integration in chat() method"""

    @pytest.mark.asyncio
    async def test_sav_workflow_continue_or_close_user_closes(self, chatbot, mock_openai_response):
        """Should close session when user wants to close"""
        chatbot.awaiting_continue_or_close = True

        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            result = await chatbot.chat("Au revoir")  # Close keyword

            # Verify session closed
            assert result["should_close_session"] is True
            assert len(chatbot.conversation_history) == 0  # Reset called

    @pytest.mark.asyncio
    async def test_sav_workflow_continue_or_close_user_continues(self, chatbot, mock_openai_response):
        """Should continue conversation when user wants to continue"""
        chatbot.awaiting_continue_or_close = True
        chatbot.should_ask_continue = True

        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            result = await chatbot.chat("Oui, je veux continuer")

            # Verify flags reset
            assert chatbot.should_ask_continue is False
            assert chatbot.awaiting_continue_or_close is False
            assert result["should_close_session"] is False

    @pytest.mark.asyncio
    async def test_sav_workflow_awaiting_confirmation_user_confirms(self, chatbot, mock_openai_response):
        """Should create ticket when user confirms validation"""
        chatbot.awaiting_confirmation = True
        chatbot.pending_ticket_validation = {
            "customer_id": "client@test.fr",
            "order_number": "CMD999",
            "product_sku": "TEST-SKU",
            "product_name": "Test Product",
            "problem_description": "Test problem description here",
            "warranty": MagicMock()
        }
        chatbot.client_data = {"amount": 1000.0}

        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)), \
             patch('app.services.chatbot.sav_workflow_engine') as mock_sav, \
             patch('app.services.chatbot.evidence_collector') as mock_ec:

            mock_ticket = MagicMock()
            mock_ticket.id = "SAV-001"
            mock_ticket.problem_category = "mechanism"
            mock_ticket.priority = "P1"
            mock_sav.process_new_claim = AsyncMock(return_value=mock_ticket)
            mock_ec.generate_evidence_request_message.return_value = "Photos"

            result = await chatbot.chat("Oui, je confirme")

            # Verify ticket created
            assert "sav_ticket" in result
            assert result["sav_ticket"] is not None
            mock_sav.process_new_claim.assert_called_once()

    @pytest.mark.asyncio
    async def test_sav_workflow_awaiting_confirmation_user_rejects(self, chatbot, mock_openai_response):
        """Should reset pending ticket when user rejects validation"""
        chatbot.awaiting_confirmation = True
        chatbot.pending_ticket_validation = {
            "order_number": "CMD999",
            "customer_id": "test@example.fr"
        }

        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)):
            result = await chatbot.chat("Non, annuler")  # Clear rejection without "correct" keyword

            # Verify pending ticket cleared
            assert chatbot.pending_ticket_validation is None
            assert chatbot.awaiting_confirmation is False

    @pytest.mark.asyncio
    async def test_sav_workflow_new_request_prepares_validation(self, chatbot, mock_openai_response):
        """Should prepare validation for new SAV request without creating ticket"""
        chatbot.conversation_type = "sav"
        order_number = "CMD123456"

        with patch.object(chatbot.client.chat.completions, 'create', new=AsyncMock(return_value=mock_openai_response)), \
             patch('app.services.warranty_service.warranty_service') as mock_ws, \
             patch('app.services.problem_detector.problem_detector') as mock_pd, \
             patch('app.services.priority_scorer.priority_scorer') as mock_ps:

            # Setup mocks
            mock_ws.create_warranty = AsyncMock(return_value=MagicMock())

            mock_problem = MagicMock()
            mock_problem.primary_category = "mechanism"
            mock_problem.severity = "P1"
            mock_problem.confidence = 0.9
            mock_pd.detect_problem_type.return_value = mock_problem

            mock_warranty_check = MagicMock()
            mock_warranty_check.is_covered = True
            mock_warranty_check.component = "Mécanisme"
            mock_ws.check_warranty_coverage.return_value = mock_warranty_check

            mock_priority = MagicMock()
            mock_priority.priority = "P1"
            mock_priority.total_score = 75
            mock_priority.explanation = "Haute"
            mock_ps.calculate_priority.return_value = mock_priority

            result = await chatbot.chat(
                "Mon canapé a un problème de mécanisme",
                order_number=order_number
            )

            # Verify validation prepared but ticket NOT created
            assert "sav_ticket" in result
            assert result["sav_ticket"] is not None
            assert result["sav_ticket"].get("validation_pending") is True
            assert chatbot.pending_ticket_validation is not None
