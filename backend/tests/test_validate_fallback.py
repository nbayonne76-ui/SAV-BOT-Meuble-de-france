import pytest
import asyncio
from datetime import datetime

from app.services.sav_workflow_engine import sav_workflow_engine, SAVTicket, TicketAction


@pytest.mark.asyncio
async def test_validate_ticket_db_fallback(monkeypatch):
    # Prepare a fake DB session with commit and refresh
    class FakeDBSession:
        async def commit(self):
            return None

        async def refresh(self, obj):
            return None

    fake_db = FakeDBSession()

    # Prepare a fake DB ticket object (ORM-like)
    class FakeDBTicket:
        def __init__(self, ticket_id):
            self.ticket_id = ticket_id
            self.status = "new"
            self.client_summary = {"validation_required": True}
            self.actions = []
            self.updated_at = None

    fake_ticket_id = "SAV-20990101-001"
    fake_db_ticket = FakeDBTicket(fake_ticket_id)

    async def fake_get_by_id(db, ticket_id):
        assert db is fake_db
        if ticket_id == fake_ticket_id:
            return fake_db_ticket
        return None

    monkeypatch.setattr("app.repositories.ticket_repository.ticket_repository.get_by_id", fake_get_by_id)

    # Ensure ticket not present in memory
    if fake_ticket_id in sav_workflow_engine.active_tickets:
        del sav_workflow_engine.active_tickets[fake_ticket_id]

    sav_workflow_engine.db_session = fake_db

    result = await sav_workflow_engine.validate_ticket(fake_ticket_id)

    assert result["success"] is True
    assert result["ticket_id"] == fake_ticket_id

    # client_summary should have been updated
    assert fake_db_ticket.client_summary.get("validation_required") is False
    assert fake_db_ticket.client_summary.get("validation_status") == "validated"

    # Action should have been appended
    assert fake_db_ticket.actions
    last_action = fake_db_ticket.actions[-1]
    assert last_action["action_type"] == "ticket_validated"


@pytest.mark.asyncio
async def test_validate_ticket_in_memory():
    # Create a minimal SAVTicket and put it in active_tickets
    ticket = SAVTicket(
        ticket_id="SAV-20990101-002",
        customer_id="CUST-TEST",
        order_number="CMD-2024-99999",
        product_sku="SKU-TEST",
        product_name="Test Product",
        problem_description="Test problem"
    )

    # Ensure no lingering state
    sav_workflow_engine.active_tickets[ticket.ticket_id] = ticket

    # Validate the ticket
    result = await sav_workflow_engine.validate_ticket(ticket.ticket_id)

    assert result["success"] is True
    assert result["ticket_id"] == ticket.ticket_id
    # Ensure ticket in memory was updated
    assert ticket.validation_status == "validated"
    assert any(a.action_type == "ticket_validated" for a in ticket.actions)

    # Cleanup
    del sav_workflow_engine.active_tickets[ticket.ticket_id]
