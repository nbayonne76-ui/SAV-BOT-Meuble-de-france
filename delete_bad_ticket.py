#!/usr/bin/env python
"""Delete corrupted ticket with null priority/status"""
import asyncio
import sys
sys.path.insert(0, 'backend')

async def delete_corrupted_ticket():
    """Delete ticket ID 123 with null values"""
    from app.db.session import AsyncSessionLocal
    from app.repositories.ticket_repository import ticket_repository

    async with AsyncSessionLocal() as db:
        # Delete the corrupted ticket
        ticket = await ticket_repository.get_by_id(db, "123")

        if ticket:
            print(f"Found corrupted ticket: {ticket.ticket_id}")
            print(f"  - Priority: {ticket.priority}")
            print(f"  - Status: {ticket.status}")

            # Delete it
            await ticket_repository.delete(db, "123")
            print("\n[SUCCESS] Deleted corrupted ticket!")
            print("\nNext steps:")
            print("1. Create a new ticket via the chat interface")
            print("2. The new ticket will have proper priority and status")
            print("3. It should appear correctly in the Dashboard")
        else:
            print("[ERROR] Ticket 123 not found")

if __name__ == "__main__":
    asyncio.run(delete_corrupted_ticket())
