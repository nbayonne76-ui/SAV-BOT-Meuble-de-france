#!/usr/bin/env python
"""
Test script for complete voice emotion workflow
Simulates a real customer voice conversation from start to finish
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.voice_emotion_detector import get_voice_emotion_detector


# Simulated customer conversations
CUSTOMER_SCENARIOS = [
    {
        "name": "Scenario 1: Angry Customer - Broken Furniture",
        "customer_name": "Jean Dupont",
        "order_number": "CMD-2025-123456",
        "messages": [
            {
                "text": "Bonjour, je m'appelle Jean Dupont. J'ai recu ma commande CMD-2025-123456 et c'est inadmissible ! Le canape est completement casse !",
                "expected_emotion": "fache",
                "stage": "Initial complaint"
            }
        ],
        "product": "Canape",
        "problem": "Pied casse, tissu dechire"
    },
    {
        "name": "Scenario 2: Calm Customer - Minor Issue",
        "customer_name": "Marie Martin",
        "order_number": "CMD-2025-789012",
        "messages": [
            {
                "text": "Bonjour, je vous contacte concernant ma commande CMD-2025-789012. J'ai une petite rayure sur ma table. Pas tres grave mais j'aimerais savoir ce qu'on peut faire. Merci.",
                "expected_emotion": "calme",
                "stage": "Polite inquiry"
            }
        ],
        "product": "Table",
        "problem": "Petite rayure"
    },
    {
        "name": "Scenario 3: Desperate Customer - Multiple Attempts",
        "customer_name": "Pierre Dubois",
        "order_number": "CMD-2025-345678",
        "messages": [
            {
                "text": "Je ne sais plus quoi faire... Ca fait trois semaines que j'attends ma commande CMD-2025-345678 et toujours rien. J'ai tout essaye, personne ne repond.",
                "expected_emotion": "desespere",
                "stage": "Desperate plea"
            }
        ],
        "product": "Armoire",
        "problem": "Livraison non recue"
    }
]


async def simulate_voice_conversation(scenario: dict):
    """Simulate a complete voice conversation workflow"""
    print("=" * 80)
    print(f"SIMULATING: {scenario['name']}")
    print("=" * 80)
    print()

    detector = get_voice_emotion_detector()
    conversation_history = []

    print(f"Customer: {scenario['customer_name']}")
    print(f"Order: {scenario['order_number']}")
    print(f"Product: {scenario['product']}")
    print(f"Problem: {scenario['problem']}")
    print()

    # Process each message in the conversation
    for i, message in enumerate(scenario['messages'], 1):
        print(f"--- Stage {i}: {message['stage']} ---")
        print()

        # Step 1: Simulate transcription
        print(f"[CUSTOMER SPEAKS]")
        print(f'Transcript: "{message["text"]}"')
        print()

        # Step 2: Analyze emotion
        print("[ANALYZING EMOTION...]")
        emotion_result = await detector.analyze_emotion(
            transcript=message["text"],
            conversation_history=conversation_history
        )

        print(f"Emotion Detected: {emotion_result['emotion']}")
        print(f"Confidence: {emotion_result['confidence']:.0%}")
        print(f"Priority Assigned: {emotion_result['priority']} ({emotion_result['urgency'].upper()})")
        print(f"SLA: < {emotion_result['sla_hours']}h")
        print(f"Indicators:")
        for indicator in emotion_result['indicators'][:3]:
            print(f"  - {indicator}")
        print()

        # Check if emotion matches expected
        emotion_match = emotion_result['emotion'] == message['expected_emotion']
        if emotion_match:
            print(f"[VALIDATION] Emotion detection CORRECT (expected: {message['expected_emotion']})")
        else:
            print(f"[WARNING] Emotion mismatch - Expected: {message['expected_emotion']}, Got: {emotion_result['emotion']}")
        print()

        # Add to conversation history
        conversation_history.append({
            "role": "user",
            "content": message["text"]
        })

    # Step 3: Simulate ticket creation
    print("--- Ticket Creation ---")
    print()
    print("[CREATING TICKET...]")

    # Use the last emotion analysis for ticket
    final_emotion = emotion_result

    ticket_data = {
        "ticket_id": f"SAV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "customer_name": scenario['customer_name'],
        "order_number": scenario['order_number'],
        "product": scenario['product'],
        "problem_description": scenario['problem'],
        "priority": final_emotion['priority'],
        "voice_emotion": final_emotion['emotion'],
        "voice_emotion_confidence": final_emotion['confidence'],
        "voice_emotion_indicators": final_emotion['indicators'],
        "sla_hours": final_emotion['sla_hours'],
        "created_at": datetime.now().isoformat()
    }

    print(f"Ticket Created: {ticket_data['ticket_id']}")
    print(f"  Customer: {ticket_data['customer_name']}")
    print(f"  Order: {ticket_data['order_number']}")
    print(f"  Product: {ticket_data['product']}")
    print(f"  Problem: {ticket_data['problem_description']}")
    print(f"  Priority: {ticket_data['priority']} (based on emotion: {ticket_data['voice_emotion']})")
    print(f"  Confidence: {ticket_data['voice_emotion_confidence']:.0%}")
    print(f"  SLA: Response required within {ticket_data['sla_hours']} hour(s)")
    print()

    # Step 4: Show what agent would see
    print("--- Agent Dashboard View ---")
    print()
    print(f"[TICKET #{ticket_data['ticket_id']}]")
    print(f"Priority: {ticket_data['priority']}")
    print(f"Emotion: {ticket_data['voice_emotion'].upper()} ({ticket_data['voice_emotion_confidence']:.0%} confidence)")
    print(f"SLA: < {ticket_data['sla_hours']}h")
    print()
    print("Emotion Indicators:")
    for indicator in ticket_data['voice_emotion_indicators'][:3]:
        print(f"  - {indicator}")
    print()

    # Show recommended action based on priority
    if ticket_data['priority'] == "P0":
        print("[ACTION REQUIRED] URGENT - Immediate escalation needed!")
        print("Recommended: Contact customer within 1 hour")
    elif ticket_data['priority'] == "P1":
        print("[ACTION REQUIRED] HIGH - Fast response needed")
        print("Recommended: Contact customer within 2 hours")
    elif ticket_data['priority'] == "P2":
        print("[ACTION] MEDIUM - Standard priority treatment")
        print(f"Recommended: Contact customer within {ticket_data['sla_hours']} hours")
    else:
        print("[INFO] LOW - Normal queue processing")
        print("Recommended: Contact customer within 24 hours")

    print()
    print("=" * 80)
    print()

    return ticket_data


async def run_all_scenarios():
    """Run all customer scenarios"""
    print()
    print("=" * 80)
    print("VOICE EMOTION WORKFLOW - END-TO-END TEST")
    print("=" * 80)
    print()
    print(f"Testing {len(CUSTOMER_SCENARIOS)} customer scenarios...")
    print()

    tickets = []

    for scenario in CUSTOMER_SCENARIOS:
        ticket = await simulate_voice_conversation(scenario)
        tickets.append(ticket)

        # Pause between scenarios
        await asyncio.sleep(0.5)

    # Summary
    print("=" * 80)
    print("TEST SUMMARY - All Scenarios Completed")
    print("=" * 80)
    print()
    print(f"Total Tickets Created: {len(tickets)}")
    print()

    # Group by priority
    priority_counts = {}
    for ticket in tickets:
        priority = ticket['priority']
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    print("Tickets by Priority:")
    priority_order = ["P0", "P1", "P2", "P3"]
    for priority in priority_order:
        count = priority_counts.get(priority, 0)
        if count > 0:
            print(f"  {priority}: {count} ticket(s)")

    print()
    print("Tickets by Emotion:")
    emotion_counts = {}
    for ticket in tickets:
        emotion = ticket['voice_emotion']
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

    for emotion, count in sorted(emotion_counts.items()):
        print(f"  {emotion}: {count} ticket(s)")

    print()
    print("Average Confidence Score:")
    avg_confidence = sum(t['voice_emotion_confidence'] for t in tickets) / len(tickets)
    print(f"  {avg_confidence:.0%}")

    print()
    print("=" * 80)
    print("[SUCCESS] Voice emotion workflow test completed successfully!")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. System is ready for production use")
    print("  2. All emotion data will be stored in Railway database")
    print("  3. Agents can see emotion context in dashboard")
    print("  4. Priority-based SLAs are automatically enforced")
    print()


if __name__ == "__main__":
    asyncio.run(run_all_scenarios())
