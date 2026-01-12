#!/usr/bin/env python
"""Delete corrupted ticket 123 from database"""
import asyncio
import sys
sys.path.insert(0, 'backend')

async def delete_ticket_123():
    """Delete the corrupted ticket 123 with null priority/status"""
    from app.db.session import AsyncSessionLocal
    from app.repositories.ticket_repository import ticket_repository

    async with AsyncSessionLocal() as db:
        try:
            # Check if ticket exists
            ticket = await ticket_repository.get_by_id(db, "123")

            if ticket:
                print(f"[FOUND] Ticket 123:")
                print(f"  - Customer: {ticket.customer_name}")
                print(f"  - Order: {ticket.order_number}")
                print(f"  - Product: {ticket.product_name}")
                print(f"  - Priority: {ticket.priority}")
                print(f"  - Status: {ticket.status}")
                print()

                # Delete it
                await ticket_repository.delete(db, "123")
                print("[SUCCESS] ✅ Ticket 123 deleted from database!")
                print()
                print("Next step: Test creating a new ticket via the chatbot")
            else:
                print("[INFO] Ticket 123 not found in database (already deleted or never existed)")

        except Exception as e:
            print(f"[ERROR] Failed to delete ticket: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(delete_ticket_123())
