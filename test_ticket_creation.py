#!/usr/bin/env python3
"""
Test script for automatic ticket creation in SAV workflow
Tests the complete flow: problem report -> validation -> confirmation -> ticket creation
"""

import requests
import json
import time

API_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_ticket_creation_workflow():
    """Test the complete SAV ticket creation workflow"""

    print_section("TEST: Automatic Ticket Creation with Validation")

    # Step 1: Send initial SAV problem message
    print("📝 Step 1: Sending SAV problem report...")
    message1 = {
        "message": "Bonjour, j'ai un problème avec mon canapé OSLO. Le pied gauche s'est cassé et le canapé est instable. C'est dangereux!",
        "session_id": "test-session-001",
        "order_number": "CMD-2024-12345"
    }

    response1 = requests.post(f"{API_URL}/api/chat/", json=message1)
    print(f"Status: {response1.status_code}")

    if response1.status_code == 200:
        data1 = response1.json()
        print(f"Bot response: {data1['response'][:200]}...")
        print(f"SAV Ticket: {data1.get('sav_ticket')}")
        print(f"Ticket Data: {data1.get('ticket_data')}")

        # Check if validation is pending
        if data1.get('sav_ticket') and data1['sav_ticket'].get('validation_pending'):
            print("✅ Validation pending - chatbot should ask for confirmation")
        else:
            print("❌ No validation pending detected")
    else:
        print(f"❌ Error: {response1.text}")
        return

    time.sleep(2)

    # Step 2: User confirms with "OUI"
    print("\n📝 Step 2: User confirms with 'OUI'...")
    message2 = {
        "message": "OUI",
        "session_id": "test-session-001",
        "order_number": "CMD-2024-12345"
    }

    response2 = requests.post(f"{API_URL}/api/chat/", json=message2)
    print(f"Status: {response2.status_code}")

    if response2.status_code == 200:
        data2 = response2.json()
        print(f"Bot response: {data2['response'][:200]}...")
        print(f"\nTicket Data: {json.dumps(data2.get('ticket_data'), indent=2)}")

        # Check if ticket was created
        if data2.get('ticket_data') and data2['ticket_data'].get('ticket_id'):
            ticket_id = data2['ticket_data']['ticket_id']
            print(f"\n✅ Ticket created successfully: {ticket_id}")

            # Step 3: Verify ticket appears in dashboard
            time.sleep(1)
            print(f"\n📝 Step 3: Verifying ticket in dashboard...")
            response3 = requests.get(f"{API_URL}/api/sav/tickets")

            if response3.status_code == 200:
                data3 = response3.json()
                print(f"Total tickets in system: {data3.get('total_tickets', 0)}")

                # Look for our ticket
                tickets = data3.get('tickets', [])
                our_ticket = next((t for t in tickets if t['ticket_id'] == ticket_id), None)

                if our_ticket:
                    print(f"✅ Ticket found in dashboard!")
                    print(f"   - Priority: {our_ticket.get('priority')}")
                    print(f"   - Status: {our_ticket.get('status')}")
                    print(f"   - Problem: {our_ticket.get('problem_description')}")
                else:
                    print(f"❌ Ticket {ticket_id} not found in dashboard")
                    print(f"   Available tickets: {[t['ticket_id'] for t in tickets]}")
            else:
                print(f"❌ Error fetching tickets: {response3.status_code}")

        else:
            print("❌ No ticket data in response")
    else:
        print(f"❌ Error: {response2.text}")

    print_section("TEST COMPLETE")

def test_rejection_workflow():
    """Test when user rejects validation with 'NON'"""

    print_section("TEST: Validation Rejection Flow")

    # Step 1: Send initial SAV problem
    print("📝 Step 1: Sending SAV problem report...")
    message1 = {
        "message": "Mon canapé URBAN a une déchirure sur l'accoudoir droit.",
        "session_id": "test-session-002",
        "order_number": "CMD-2024-67890"
    }

    response1 = requests.post(f"{API_URL}/api/chat/", json=message1)
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"✅ Bot asks for validation")

    time.sleep(1)

    # Step 2: User rejects with "NON"
    print("\n📝 Step 2: User rejects with 'NON'...")
    message2 = {
        "message": "NON, ce n'est pas le bon produit",
        "session_id": "test-session-002"
    }

    response2 = requests.post(f"{API_URL}/api/chat/", json=message2)
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"Bot response: {data2['response'][:200]}...")

        # Should NOT create ticket
        if not data2.get('ticket_data'):
            print("✅ No ticket created (as expected)")
        else:
            print("❌ Ticket was created (should not happen!)")

    print_section("TEST COMPLETE")

if __name__ == "__main__":
    try:
        # Test 1: Normal flow with confirmation
        test_ticket_creation_workflow()

        time.sleep(3)

        # Test 2: Rejection flow
        test_rejection_workflow()

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running on http://localhost:8000?")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
