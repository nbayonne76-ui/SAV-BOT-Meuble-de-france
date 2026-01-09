"""
Test script to create a ticket and verify database persistence
"""
import requests
import json
from datetime import datetime, timedelta

API_URL = "http://127.0.0.1:8000"

def test_create_ticket():
    """Create a test SAV ticket"""

    # Sample ticket data
    ticket_data = {
        "customer_id": "CUST-TEST-001",
        "order_number": "CMD-2024-99999",
        "product_sku": "MDF-CAP-TEST-01",
        "product_name": "Canapé TEST",
        "problem_description": "Le canapé présente un affaissement important des coussins après seulement 3 mois d'utilisation normale. C'est vraiment frustrant !",
        "purchase_date": (datetime.now() - timedelta(days=90)).isoformat(),
        "delivery_date": (datetime.now() - timedelta(days=85)).isoformat(),
        "customer_tier": "premium",
        "product_value": 1500.0
    }

    print("TEST 1: Creating a SAV ticket...")
    print(f"Order: {ticket_data['order_number']}")
    print(f"Product: {ticket_data['product_name']}")
    print(f"Problem: {ticket_data['problem_description'][:50]}...")

    try:
        response = requests.post(
            f"{API_URL}/api/sav/create-claim",
            json=ticket_data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            ticket_id = result['ticket']['ticket_id']
            print(f"\n[SUCCESS] Ticket created successfully!")
            print(f"Ticket ID: {ticket_id}")
            print(f"Priority: {result['ticket']['priority']}")
            print(f"Status: {result['ticket']['status']}")
            print(f"Auto-resolved: {result['ticket']['auto_resolved']}")
            return ticket_id
        else:
            print(f"\n[ERROR] Error creating ticket: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        return None

def test_fetch_tickets():
    """Fetch all tickets from dashboard endpoint"""

    print("\nTEST 2: Fetching tickets from dashboard...")

    try:
        response = requests.get(
            f"{API_URL}/api/sav/tickets",
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            total = result['total_tickets']
            tickets = result['tickets']

            print(f"\n[SUCCESS] Successfully fetched tickets from database!")
            print(f"Total tickets: {total}")

            if tickets:
                print("\nTicket List:")
                for i, ticket in enumerate(tickets[:5], 1):  # Show first 5
                    print(f"\n  {i}. Ticket ID: {ticket['ticket_id']}")
                    print(f"     Customer: {ticket.get('customer_name', 'N/A')}")
                    print(f"     Order: {ticket['order_number']}")
                    print(f"     Product: {ticket['product_name']}")
                    print(f"     Priority: {ticket['priority']}")
                    print(f"     Status: {ticket['status']}")
                    print(f"     Created: {ticket['created_at']}")
            else:
                print("\n[WARNING] No tickets found in database")

            return total > 0
        else:
            print(f"\n[ERROR] Error fetching tickets: {response.status_code}")
            return False

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        return False

def main():
    print("=" * 60)
    print("TESTING TICKET PERSISTENCE TO DATABASE")
    print("=" * 60)

    # Test 1: Create ticket
    ticket_id = test_create_ticket()

    if not ticket_id:
        print("\n[FAILED] Test failed: Could not create ticket")
        return

    # Test 2: Fetch tickets
    success = test_fetch_tickets()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    if success:
        print("[PASS] All tests passed!")
        print("[PASS] Tickets are persisted to database")
        print("[PASS] Dashboard can fetch tickets from database")
        print("\n[SUCCESS] Ready for Railway deployment!")
    else:
        print("[FAIL] Tests failed")
        print("[WARNING] Check the backend logs for errors")

    print("=" * 60)

if __name__ == "__main__":
    main()
