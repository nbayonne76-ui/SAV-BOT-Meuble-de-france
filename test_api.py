#!/usr/bin/env python
"""Test script to check tickets API"""
import asyncio
import sys
sys.path.insert(0, 'backend')

async def test_tickets_api():
    """Test if tickets are in database"""
    from app.db.session import AsyncSessionLocal
    from app.repositories.ticket_repository import ticket_repository

    async with AsyncSessionLocal() as db:
        # Get all tickets
        tickets = await ticket_repository.get_all(db, limit=100)

        print(f"\n{'='*60}")
        print(f"[TICKETS] DATABASE COUNT: {len(tickets)}")
        print(f"{'='*60}\n")

        if tickets:
            for i, ticket in enumerate(tickets, 1):
                print(f"{i}. Ticket ID: {ticket.ticket_id}")
                print(f"   Customer: {ticket.customer_name or 'N/A'}")
                print(f"   Product: {ticket.product_name or 'N/A'}")
                print(f"   Status: {ticket.status}")
                print(f"   Priority: {ticket.priority}")
                print(f"   Created: {ticket.created_at}")
                print()
        else:
            print("[ERROR] NO TICKETS FOUND IN DATABASE!")
            print("\nPossible reasons:")
            print("1. No tickets have been created yet")
            print("2. Tickets were created but not saved (the bug we just fixed)")
            print("3. Database connection issue")
            print("\nTo test:")
            print("- Create a ticket via the chatbot")
            print("- Run this script again to verify it was saved")

if __name__ == "__main__":
    asyncio.run(test_tickets_api())
