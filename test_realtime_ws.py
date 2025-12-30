#!/usr/bin/env python3
"""
Script de test pour WebSocket Realtime API
"""
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
        print("❌ OPENAI_API_KEY non définie")
        return

    print(f"✅ Clé API trouvée: {api_key[:20]}...")

    # URL de l'API Realtime
    realtime_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1"
    }

    print(f"\n🔌 Connexion à {realtime_url}...")

    try:
        async with websockets.connect(realtime_url, additional_headers=headers) as ws:
            print("✅ Connecté à OpenAI Realtime API!")

            # Configurer la session
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text"],  # Commencer avec text seulement pour simplifier
                    "instructions": "Tu es un assistant SAV. Réponds brièvement.",
                    "temperature": 0.7,
                }
            }

            print("\n📤 Envoi configuration session...")
            await ws.send(json.dumps(session_config))

            # Écouter les réponses pendant 5 secondes
            print("\n📥 Écoute des événements...")
            timeout_counter = 0
            max_timeout = 10  # 10 secondes max

            while timeout_counter < max_timeout:
                try:
                    # Attendre un message avec timeout de 1 seconde
                    message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    event = json.loads(message)

                    print(f"\n📨 Event reçu: {event.get('type', 'unknown')}")

                    if event.get('type') == 'error':
                        print(f"❌ Erreur: {event.get('error', {})}")
                        break
                    elif event.get('type') == 'session.created':
                        print("✅ Session créée!")
                        print(f"   Détails: {json.dumps(event.get('session', {}), indent=2)}")
                    elif event.get('type') == 'session.updated':
                        print("✅ Session mise à jour!")

                        # Maintenant envoyer un message de test
                        print("\n📤 Envoi message test: 'Bonjour'")
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

                        # Demander une réponse
                        await ws.send(json.dumps({"type": "response.create"}))
                    else:
                        print(f"   Data: {json.dumps(event, indent=2)[:200]}...")

                except asyncio.TimeoutError:
                    timeout_counter += 1
                    print(f"⏱️  Timeout {timeout_counter}/{max_timeout}...")
                except websockets.exceptions.ConnectionClosed:
                    print("🔌 Connexion fermée par le serveur")
                    break

            print("\n✅ Test terminé")

    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Erreur de statut HTTP: {e}")
        print(f"   Statut: {e.status_code}")
        print(f"   Vérifiez que votre clé API a accès à l'API Realtime")
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ Erreur WebSocket: {e}")
    except Exception as e:
        print(f"❌ Erreur: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("Test de connexion OpenAI Realtime API\n")
    asyncio.run(test_realtime_api())
