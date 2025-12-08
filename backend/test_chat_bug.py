#!/usr/bin/env python3
"""
Test script to reproduce the chat bug
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.chatbot import MeubledeFranceChatbot
from app.core.config import settings

# Global instance like in chat.py
chatbot_instances = {}

async def test_chat_like_api():
    """Reproduce exactly what the API does"""

    session_id = "test_session"

    print("=" * 60)
    print("TEST: Creating chatbot instance (like API does)")
    print("=" * 60)

    try:
        # Exactly like chat.py line 38-44
        if session_id not in chatbot_instances:
            print(f"Creating new chatbot instance for session: {session_id}")
            chatbot_instances[session_id] = MeubledeFranceChatbot(
                api_key=settings.OPENAI_API_KEY
            )

        chatbot = chatbot_instances[session_id]
        print(f"OK Chatbot instance obtained")

        # Call chat method
        print("\n" + "=" * 60)
        print("TEST: Calling chatbot.chat() with simple message")
        print("=" * 60)

        result = await chatbot.chat(
            user_message="Bonjour",
            order_number=None,
            photos=[]
        )

        if "error" in result:
            print(f"\nERROR returned by chatbot:")
            print(f"   Error: {result.get('error')}")
            print(f"   Response: {result.get('response')}")
            return False
        else:
            print(f"\nSUCCESS:")
            print(f"   Response: {result['response'][:100]}...")
            return True

    except Exception as e:
        print(f"\nEXCEPTION raised:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        import traceback
        print(f"\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing chat functionality like the API does...\n")
    success = asyncio.run(test_chat_like_api())

    if success:
        print("\n" + "=" * 60)
        print("TEST PASSED - No issues found")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("TEST FAILED - Issue reproduced!")
        print("=" * 60)
        sys.exit(1)
