#!/usr/bin/env python3
"""Script de test pour WebSocket Realtime API"""
import asyncio
import websockets
import json
import os
import sys

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

async def test_realtime_api():
    """Test direct de l'OpenAI Realtime API"""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("[ERROR] OPENAI_API_KEY non definie")
        return

    print(f"[OK] Cle API trouvee: {api_key[:20]}...")

    # URL de l'API Realtime
    realtime_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1"
    }

    print(f"\n[CONNECT] Connexion a {realtime_url}...")

    try:
        async with websockets.connect(realtime_url, additional_headers=headers) as ws:
            print("[OK] Connecte a OpenAI Realtime API!")

            # Configurer la session
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text"],
                    "instructions": "Tu es un assistant SAV. Reponds brievement.",
                    "temperature": 0.7,
                }
            }

            print("\n[SEND] Envoi configuration session...")
            await ws.send(json.dumps(session_config))

            # Écouter les réponses pendant quelques secondes
            print("\n[LISTEN] Ecoute des evenements...")
            timeout_counter = 0
            max_timeout = 10

            while timeout_counter < max_timeout:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    event = json.loads(message)

                    print(f"\n[EVENT] Event recu: {event.get('type', 'unknown')}")

                    if event.get('type') == 'error':
                        print(f"[ERROR] Erreur: {event.get('error', {})}")
                        break
                    elif event.get('type') == 'session.created':
                        print("[OK] Session creee!")
                    elif event.get('type') == 'session.updated':
                        print("[OK] Session mise a jour!")

                        # Envoyer un message de test
                        print("\n[SEND] Envoi message test: 'Bonjour'")
                        test_message = {
                            "type": "conversation.item.create",
                            "item": {
                                "type": "message",
                                "role": "user",
                                "content": [{
                                    "type": "input_text",
                                    "text": "Bonjour"
                                }]
                            }
                        }
                        await ws.send(json.dumps(test_message))
                        await ws.send(json.dumps({"type": "response.create"}))
                    elif event.get('type') == 'response.done':
                        print("[OK] Reponse complete recue!")
                        # Afficher la réponse
                        if 'response' in event and 'output' in event['response']:
                            for output in event['response']['output']:
                                if output.get('type') == 'message':
                                    for content in output.get('content', []):
                                        if content.get('type') == 'text':
                                            print(f"[RESPONSE] {content.get('text', '')}")
                        timeout_counter = max_timeout  # Arrêter après la première réponse
                    else:
                        print(f"   [DATA] {str(event)[:200]}...")

                except asyncio.TimeoutError:
                    timeout_counter += 1
                    print(f"[TIMEOUT] {timeout_counter}/{max_timeout}...")
                except websockets.exceptions.ConnectionClosed:
                    print("[CLOSE] Connexion fermee par le serveur")
                    break

            print("\n[OK] Test termine")

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"[ERROR] Erreur de statut HTTP: {e}")
        print(f"   Statut: {e.status_code}")
        print(f"   Verifiez que votre cle API a acces a l'API Realtime")
    except websockets.exceptions.WebSocketException as e:
        print(f"[ERROR] Erreur WebSocket: {e}")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("=== Test de connexion OpenAI Realtime API ===\n")
    asyncio.run(test_realtime_api())
