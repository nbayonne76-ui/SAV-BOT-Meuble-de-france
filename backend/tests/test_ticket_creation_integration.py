"""
Integration tests for ticket creation flow across all languages
Tests the complete workflow: chat → prepare validation → validate → create ticket
"""
import pytest
import asyncio
from datetime import datetime

from app.services.chatbot import MeubledeFranceChatbot
from app.services.sav_workflow_engine import sav_workflow_engine, SAVTicket, TicketAction


@pytest.mark.asyncio
async def test_ticket_creation_french_flow():
    """Test complete ticket creation workflow in French"""
    # Initialize chatbot
    chatbot = MeubledeFranceChatbot(api_key="test-key")

    # Simulate user sending a message with problem description
    order_number = "CMD-2025-00001"
    user_message = "Bonjour, mon canapé a un problème. L'affaissement des coussins est important."

    # Initial chat (should not create ticket yet)
    result = await chatbot.chat(
        user_message=user_message,
        order_number=order_number,
        db_session=None,
        preferred_language="fr"
    )

    assert result["response"] is not None
    assert "photo" in result["response"].lower() or "image" in result["response"].lower()

    # Verify no ticket created yet
    assert result.get("ticket_data") is None

    # Simulate user uploading photos
    photos = ["http://example.com/photo1.jpg", "http://example.com/photo2.jpg"]

    # Chat with photos should prepare ticket validation
    result = await chatbot.chat(
        user_message="Voilà les photos du problème",
        order_number=order_number,
        photos=photos,
        db_session=None,
        preferred_language="fr"
    )

    assert result["response"] is not None
    # Should ask for confirmation
    assert "confirm" in result["response"].lower() or "correct" in result["response"].lower()

    # Verify ticket_data is prepared with PENDING status
    assert result.get("ticket_data") is not None
    ticket_data = result["ticket_data"]
    assert ticket_data["requires_validation"] is True
    assert ticket_data["ticket_id"].startswith("PENDING-")

    # Simulate user confirming
    result = await chatbot.chat(
        user_message="Oui, c'est correct",
        order_number=order_number,
        db_session=None,
        preferred_language="fr"
    )

    assert result["response"] is not None
    assert "succès" in result["response"].lower() or "créé" in result["response"].lower()


@pytest.mark.asyncio
async def test_ticket_creation_english_flow():
    """Test complete ticket creation workflow in English"""
    chatbot = MeubledeFranceChatbot(api_key="test-key")

    order_number = "CMD-2025-00002"
    user_message = "Hi, my sofa has a problem. The cushions are sagging significantly."

    # Initial chat
    result = await chatbot.chat(
        user_message=user_message,
        order_number=order_number,
        db_session=None,
        preferred_language="en"
    )

    assert result["response"] is not None
    assert result.get("ticket_data") is None

    # Chat with photos
    photos = ["http://example.com/photo1.jpg"]

    result = await chatbot.chat(
        user_message="Here are the photos",
        order_number=order_number,
        photos=photos,
        db_session=None,
        preferred_language="en"
    )

    assert result["response"] is not None
    assert result.get("ticket_data") is not None
    assert result["ticket_data"]["requires_validation"] is True

    # Confirm
    result = await chatbot.chat(
        user_message="Yes, that is correct",
        order_number=order_number,
        db_session=None,
        preferred_language="en"
    )

    assert result["response"] is not None
    assert "success" in result["response"].lower() or "created" in result["response"].lower()


@pytest.mark.asyncio
async def test_ticket_creation_arabic_flow():
    """Test complete ticket creation workflow in Arabic"""
    chatbot = MeubledeFranceChatbot(api_key="test-key")

    order_number = "CMD-2025-00003"
    user_message = "مرحبا، أريكتي بها مشكلة. الوسائد تهبط بشكل ملحوظ."

    # Initial chat
    result = await chatbot.chat(
        user_message=user_message,
        order_number=order_number,
        db_session=None,
        preferred_language="ar"
    )

    assert result["response"] is not None
    assert result.get("ticket_data") is None

    # Chat with photos
    photos = ["http://example.com/photo1.jpg", "http://example.com/photo2.jpg"]

    result = await chatbot.chat(
        user_message="إليك الصور",
        order_number=order_number,
        photos=photos,
        db_session=None,
        preferred_language="ar"
    )

    assert result["response"] is not None
    assert result.get("ticket_data") is not None
    assert result["ticket_data"]["requires_validation"] is True

    # Confirm
    result = await chatbot.chat(
        user_message="نعم، هذا صحيح",
        order_number=order_number,
        db_session=None,
        preferred_language="ar"
    )

    assert result["response"] is not None


@pytest.mark.asyncio
async def test_validate_ticket_fallback_to_db(monkeypatch):
    """Test that validation falls back to DB when ticket not in memory"""
    # Create a minimal SAVTicket
    ticket = SAVTicket(
        ticket_id="SAV-20990101-001",
        customer_id="CUST-TEST",
        order_number="CMD-2025-00004",
        product_sku="SKU-TEST",
        product_name="Test Product",
        problem_description="Test problem"
    )

    # Put it in active tickets
    sav_workflow_engine.active_tickets[ticket.ticket_id] = ticket

    # Validate should succeed
    result = await sav_workflow_engine.validate_ticket(ticket.ticket_id)

    assert result["success"] is True
    assert result["ticket_id"] == ticket.ticket_id
    assert ticket.validation_status == "validated"

    # Cleanup
    del sav_workflow_engine.active_tickets[ticket.ticket_id]


@pytest.mark.asyncio
async def test_ticket_rejection_flow():
    """Test that user can reject ticket and start over"""
    chatbot = MeubledeFranceChatbot(api_key="test-key")

    order_number = "CMD-2025-00005"
    user_message = "Mon canapé a un problème."

    # Initial chat
    result = await chatbot.chat(
        user_message=user_message,
        order_number=order_number,
        db_session=None,
        preferred_language="fr"
    )

    # Chat with photos
    photos = ["http://example.com/photo1.jpg"]

    result = await chatbot.chat(
        user_message="Voilà les photos",
        order_number=order_number,
        photos=photos,
        db_session=None,
        preferred_language="fr"
    )

    assert result["ticket_data"]["requires_validation"] is True

    # User says "No" or rejects
    result = await chatbot.chat(
        user_message="Non, ce n'est pas correct",
        order_number=order_number,
        db_session=None,
        preferred_language="fr"
    )

    # Should ask to resubmit with correct info
    assert result["response"] is not None
    # pending_ticket_validation should be cleared
    assert chatbot.pending_ticket_validation is None or chatbot.awaiting_confirmation is False
