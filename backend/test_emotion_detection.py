#!/usr/bin/env python
"""
Test script for voice emotion detection system
Tests various customer scenarios to verify emotion detection accuracy
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.voice_emotion_detector import get_voice_emotion_detector


# Test scenarios
TEST_SCENARIOS = [
    {
        "name": "Angry Customer - Explicit",
        "text": "C'est inadmissible ! Mon canapé est complètement cassé et personne ne répond ! Je suis furieux !",
        "expected_emotion": "fache",
        "expected_priority": "P0"
    },
    {
        "name": "Angry Customer - Strong Language",
        "text": "C'est une honte ! Vous m'avez livré un meuble défectueux ! C'est inacceptable !",
        "expected_emotion": "fache",
        "expected_priority": "P0"
    },
    {
        "name": "Irritated Customer",
        "text": "Je suis vraiment énervé, ça fait trois fois que j'appelle et toujours pas de solution. C'est frustrant.",
        "expected_emotion": "enerve",
        "expected_priority": "P1"
    },
    {
        "name": "Desperate Customer",
        "text": "Je ne sais plus quoi faire... J'ai tout essayé et rien ne fonctionne. Je suis désespéré.",
        "expected_emotion": "desespere",
        "expected_priority": "P2"
    },
    {
        "name": "Sad Customer",
        "text": "Je suis vraiment déçu, j'attendais tellement ce meuble et il est arrivé abîmé. C'est triste.",
        "expected_emotion": "triste",
        "expected_priority": "P2"
    },
    {
        "name": "Calm Customer",
        "text": "Bonjour, j'ai un petit problème avec ma table. Pas urgent, mais j'aimerais bien avoir votre avis. Merci beaucoup.",
        "expected_emotion": "calme",
        "expected_priority": "P3"
    },
    {
        "name": "Polite Customer",
        "text": "Bonjour, je vous contacte concernant ma commande. Je comprends que vous êtes occupés. Merci de me rappeler quand vous pourrez.",
        "expected_emotion": "calme",
        "expected_priority": "P3"
    },
    {
        "name": "Mixed Emotion - Angry then Calm",
        "text": "Au début j'étais furieux mais maintenant je comprends que ce sont des choses qui arrivent. Merci pour votre écoute.",
        "expected_emotion": "calme",  # Should detect most recent emotion
        "expected_priority": "P3"
    }
]


async def test_emotion_detection():
    """Run all test scenarios"""
    print("=" * 80)
    print("VOICE EMOTION DETECTION SYSTEM - TEST SUITE")
    print("=" * 80)
    print()

    detector = get_voice_emotion_detector()

    results = []
    total_tests = len(TEST_SCENARIOS)
    passed_tests = 0

    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"[Test {i}/{total_tests}] {scenario['name']}")
        print(f"   Input: \"{scenario['text'][:60]}...\"")

        try:
            # Analyze emotion
            result = await detector.analyze_emotion(
                transcript=scenario['text'],
                conversation_history=[]
            )

            # Check results
            emotion_match = result['emotion'] == scenario['expected_emotion']
            priority_match = result['priority'] == scenario['expected_priority']
            test_passed = emotion_match and priority_match

            if test_passed:
                passed_tests += 1
                status = "[PASSED]"
            else:
                status = "[FAILED]"

            print(f"   {status}")
            print(f"   Detected: {result['emotion']} (expected: {scenario['expected_emotion']})")
            print(f"   Priority: {result['priority']} (expected: {scenario['expected_priority']})")
            print(f"   Confidence: {result['confidence']:.2%}")
            print(f"   Indicators: {', '.join(result['indicators'][:2])}")
            print()

            results.append({
                'scenario': scenario['name'],
                'passed': test_passed,
                'detected': result['emotion'],
                'expected': scenario['expected_emotion'],
                'confidence': result['confidence']
            })

        except Exception as e:
            print(f"   [ERROR]: {e}")
            print()
            results.append({
                'scenario': scenario['name'],
                'passed': False,
                'error': str(e)
            })

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"Failed: {total_tests - passed_tests}")
    print()

    # Detailed results
    print("Detailed Results:")
    for result in results:
        if result['passed']:
            print(f"  [PASS] {result['scenario']}")
        else:
            if 'error' in result:
                print(f"  [FAIL] {result['scenario']} - Error: {result['error']}")
            else:
                print(f"  [FAIL] {result['scenario']} - Expected: {result['expected']}, Got: {result['detected']}")

    print()
    print("=" * 80)

    if passed_tests == total_tests:
        print("[SUCCESS] ALL TESTS PASSED! Emotion detection system is working correctly.")
    elif passed_tests >= total_tests * 0.75:
        print("[WARNING] Most tests passed. Review failed cases for potential improvements.")
    else:
        print("[ERROR] Multiple tests failed. System needs adjustment.")

    print("=" * 80)

    return passed_tests == total_tests


async def test_single_emotion(text: str):
    """Test a single text input"""
    print("=" * 80)
    print("SINGLE EMOTION TEST")
    print("=" * 80)
    print()
    print(f"Input: \"{text}\"")
    print()

    detector = get_voice_emotion_detector()
    result = await detector.analyze_emotion(transcript=text, conversation_history=[])

    print(f"Emotion: {result['emotion']}")
    print(f"Priority: {result['priority']} ({result['urgency'].upper()})")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"SLA: < {result['sla_hours']}h")
    print(f"Description: {result['description']}")
    print()
    print("Indicators:")
    for indicator in result['indicators']:
        print(f"  - {indicator}")
    print()
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test custom text
        custom_text = " ".join(sys.argv[1:])
        asyncio.run(test_single_emotion(custom_text))
    else:
        # Run full test suite
        asyncio.run(test_emotion_detection())
