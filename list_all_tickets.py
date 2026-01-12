#!/usr/bin/env python
"""List all tickets in database to identify corrupted ones"""
import asyncio
import sys
sys.path.insert(0, 'backend')

async def list_all_tickets():
    """List all tickets in the database"""
    from app.db.session import AsyncSessionLocal
    from sqlalchemy import select, text
    from app.models.ticket import TicketDB

    async with AsyncSessionLocal() as db:
        try:
            # Get all tickets
            result = await db.execute(
                select(TicketDB).order_by(TicketDB.created_at.desc())
            )
            tickets = result.scalars().all()

            print(f"[DATABASE] Total tickets: {len(tickets)}")
            print()

            if not tickets:
                print("[INFO] No tickets found in database")
                return

            for ticket in tickets:
                print(f"Ticket ID: {ticket.ticket_id}")
                print(f"  Customer: {ticket.customer_name}")
                print(f"  Order: {ticket.order_number}")
                print(f"  Product: {ticket.product_name}")
                print(f"  Problem: {ticket.problem_description}")
                print(f"  Priority: {ticket.priority} {'⚠️ NULL!' if ticket.priority is None else ''}")
                print(f"  Status: {ticket.status} {'⚠️ NULL!' if ticket.status is None else ''}")
                print(f"  Created: {ticket.created_at}")
                print()

        except Exception as e:
            print(f"[ERROR] Failed to list tickets: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(list_all_tickets())
