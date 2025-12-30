#!/usr/bin/env python3
"""
Tests avancés de conversations vocales
Scénarios plus complexes et réalistes
"""
import asyncio
import aiohttp
import json
import time
import sys
import io

# Fix encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API_URL = "http://localhost:8000"


class ConversationSimulator:
    """Simule une conversation vocale complète"""

    def __init__(self, scenario_name: str):
        self.scenario_name = scenario_name
        self.start_time = None
        self.end_time = None
        self.latencies = []
        self.exchanges = 0

    async def send_message(self, session, message: str, conversation_history: list = None):
        """Envoie un message à l'API et mesure la latence"""
        if conversation_history is None:
            conversation_history = []

        start = time.time()

        async with session.post(
            f"{API_URL}/api/voice/chat",
            json={
                "message": message,
                "conversation_history": conversation_history
            }
        ) as resp:
            data = await resp.json()
            latency = time.time() - start
            self.latencies.append(latency)
            self.exchanges += 1

            return {
                "response": data["response"],
                "action": data.get("action"),
                "ticket_data": data.get("ticket_data"),
                "latency": latency
            }

    def print_message(self, role: str, content: str, latency: float = None):
        """Affiche un message de conversation"""
        if role == "user":
            print(f"  👤 USER: {content}")
        else:
            lat_str = f" ({latency:.2f}s)" if latency else ""
            print(f"  🤖 ASSISTANT{lat_str}: {content}")

    def print_summary(self):
        """Affiche le résumé des performances"""
        duration = self.end_time - self.start_time
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        min_latency = min(self.latencies) if self.latencies else 0
        max_latency = max(self.latencies) if self.latencies else 0

        print(f"\n📊 RÉSUMÉ - {self.scenario_name}")
        print(f"  • Durée totale: {duration:.2f}s")
        print(f"  • Nombre d'échanges: {self.exchanges}")
        print(f"  • Latence moyenne: {avg_latency:.2f}s")
        print(f"  • Latence min: {min_latency:.2f}s")
        print(f"  • Latence max: {max_latency:.2f}s")
        print()


async def scenario_1_tout_dun_coup(session):
    """Client qui donne TOUTES les informations d'un seul coup"""
    print("="*70)
    print("🧪 SCÉNARIO 1: Client qui donne tout d'un coup")
    print("="*70)

    sim = ConversationSimulator("Scénario 1")
    sim.start_time = time.time()
    conversation_history = []

    # Message initial du bot
    resp = await sim.send_message(session, "Bonjour", conversation_history)
    sim.print_message("user", "Bonjour")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "Bonjour"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})
    await asyncio.sleep(0.5)

    # Le client donne TOUT d'un coup!
    message = "Oui bonjour, c'est Thomas Renard, j'ai commandé un canapé OSLO avec le numéro CMD-2024-88888 et malheureusement le pied gauche est cassé"
    resp = await sim.send_message(session, message, conversation_history)
    sim.print_message("user", message)
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": message})
    conversation_history.append({"role": "assistant", "content": resp["response"]})

    # Vérifier si le bot fait directement le récapitulatif
    if "Je récapitule" in resp["response"]:
        print("\n  ✅ EXCELLENT! Le bot a détecté les 4 informations d'un coup!")
        await asyncio.sleep(0.5)

        # Confirmation
        resp = await sim.send_message(session, "Oui parfait", conversation_history)
        sim.print_message("user", "Oui parfait")
        sim.print_message("assistant", resp["response"], resp["latency"])

        success = resp["action"] == "create_ticket"
    else:
        print("\n  ⚠️ Le bot n'a pas détecté toutes les infos, il continue à poser des questions")
        success = False

    sim.end_time = time.time()
    sim.print_summary()

    return success


async def scenario_2_langage_familier(session):
    """Client qui utilise un langage très familier"""
    print("="*70)
    print("🧪 SCÉNARIO 2: Client avec langage familier")
    print("="*70)

    sim = ConversationSimulator("Scénario 2")
    sim.start_time = time.time()
    conversation_history = []

    # Début
    resp = await sim.send_message(session, "Salut", conversation_history)
    sim.print_message("user", "Salut")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "Salut"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})
    await asyncio.sleep(0.5)

    # Nom très familier
    resp = await sim.send_message(session, "Ouais moi c'est Kevin Dubois", conversation_history)
    sim.print_message("user", "Ouais moi c'est Kevin Dubois")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "Ouais moi c'est Kevin Dubois"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})
    await asyncio.sleep(0.5)

    # Problème familier
    resp = await sim.send_message(session, "Bah en fait ma table elle a une grosse rayure quoi", conversation_history)
    sim.print_message("user", "Bah en fait ma table elle a une grosse rayure quoi")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "Bah en fait ma table elle a une grosse rayure quoi"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})
    await asyncio.sleep(0.5)

    # Produit
    resp = await sim.send_message(session, "C'est la table NORDIC", conversation_history)
    sim.print_message("user", "C'est la table NORDIC")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "C'est la table NORDIC"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})
    await asyncio.sleep(0.5)

    # Commande
    resp = await sim.send_message(session, "CMD-2024-44444", conversation_history)
    sim.print_message("user", "CMD-2024-44444")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "CMD-2024-44444"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})

    if "Je récapitule" in resp["response"]:
        print("\n  ✅ Récapitulatif détecté!")
        await asyncio.sleep(0.5)

        resp = await sim.send_message(session, "Ouais c'est bon", conversation_history)
        sim.print_message("user", "Ouais c'est bon")
        sim.print_message("assistant", resp["response"], resp["latency"])
        success = resp["action"] == "create_ticket"
    else:
        success = False

    sim.end_time = time.time()
    sim.print_summary()

    return success


async def scenario_3_client_impatient(session):
    """Client pressé qui veut aller vite"""
    print("="*70)
    print("🧪 SCÉNARIO 3: Client très impatient")
    print("="*70)

    sim = ConversationSimulator("Scénario 3")
    sim.start_time = time.time()
    conversation_history = []

    # Le client donne son nom directement
    resp = await sim.send_message(session, "Julie Martin", conversation_history)
    sim.print_message("user", "Julie Martin")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "Julie Martin"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})
    await asyncio.sleep(0.3)

    # Réponse ultra-courte
    resp = await sim.send_message(session, "Pied cassé", conversation_history)
    sim.print_message("user", "Pied cassé")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "Pied cassé"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})
    await asyncio.sleep(0.3)

    # Ultra-court
    resp = await sim.send_message(session, "Fauteuil RELAX", conversation_history)
    sim.print_message("user", "Fauteuil RELAX")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "Fauteuil RELAX"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})
    await asyncio.sleep(0.3)

    # Juste le numéro
    resp = await sim.send_message(session, "CMD-2024-99999", conversation_history)
    sim.print_message("user", "CMD-2024-99999")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "CMD-2024-99999"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})

    if "Je récapitule" in resp["response"]:
        print("\n  ✅ Le bot a géré les réponses ultra-courtes!")
        await asyncio.sleep(0.3)

        resp = await sim.send_message(session, "OK", conversation_history)
        sim.print_message("user", "OK")
        sim.print_message("assistant", resp["response"], resp["latency"])
        success = resp["action"] == "create_ticket"
    else:
        success = False

    sim.end_time = time.time()
    sim.print_summary()

    return success


async def scenario_4_numero_en_premier(session):
    """Client qui commence par donner son numéro de commande"""
    print("="*70)
    print("🧪 SCÉNARIO 4: Client qui donne le numéro de commande en premier")
    print("="*70)

    sim = ConversationSimulator("Scénario 4")
    sim.start_time = time.time()
    conversation_history = []

    # Le client donne directement son numéro
    message = "Bonjour, ma commande c'est CMD-2024-66666"
    resp = await sim.send_message(session, message, conversation_history)
    sim.print_message("user", message)
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": message})
    conversation_history.append({"role": "assistant", "content": resp["response"]})

    # Le bot devrait demander le nom
    print("  ℹ️  Le bot devrait demander le nom maintenant...")
    await asyncio.sleep(0.5)

    # Nom
    resp = await sim.send_message(session, "Isabelle Rousseau", conversation_history)
    sim.print_message("user", "Isabelle Rousseau")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "Isabelle Rousseau"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})
    await asyncio.sleep(0.5)

    # Problème
    resp = await sim.send_message(session, "Mon armoire a les portes mal alignées", conversation_history)
    sim.print_message("user", "Mon armoire a les portes mal alignées")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "Mon armoire a les portes mal alignées"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})
    await asyncio.sleep(0.5)

    # Produit
    resp = await sim.send_message(session, "Armoire ELEGANCE", conversation_history)
    sim.print_message("user", "Armoire ELEGANCE")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "Armoire ELEGANCE"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})

    if "Je récapitule" in resp["response"]:
        print("\n  ✅ Le bot a bien géré l'ordre différent!")
        await asyncio.sleep(0.5)

        resp = await sim.send_message(session, "Oui", conversation_history)
        sim.print_message("user", "Oui")
        sim.print_message("assistant", resp["response"], resp["latency"])
        success = resp["action"] == "create_ticket"
    else:
        success = False

    sim.end_time = time.time()
    sim.print_summary()

    return success


async def scenario_5_probleme_complexe(session):
    """Client avec un problème complexe décrit en détail"""
    print("="*70)
    print("🧪 SCÉNARIO 5: Client avec problème complexe")
    print("="*70)

    sim = ConversationSimulator("Scénario 5")
    sim.start_time = time.time()
    conversation_history = []

    # Bonjour
    resp = await sim.send_message(session, "Bonjour", conversation_history)
    sim.print_message("user", "Bonjour")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "Bonjour"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})
    await asyncio.sleep(0.5)

    # Nom
    resp = await sim.send_message(session, "Marc Lefevre", conversation_history)
    sim.print_message("user", "Marc Lefevre")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "Marc Lefevre"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})
    await asyncio.sleep(0.5)

    # Problème complexe
    message = "Alors voilà, j'ai mon canapé qui fait un bruit bizarre quand on s'assoit, ça grince énormément, on dirait que c'est la structure en bois qui bouge"
    resp = await sim.send_message(session, message, conversation_history)
    sim.print_message("user", message)
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": message})
    conversation_history.append({"role": "assistant", "content": resp["response"]})

    # Vérifier si le bot a bien synthétisé le problème
    print("  ℹ️  Le bot devrait synthétiser: 'canapé qui grince'")
    await asyncio.sleep(0.5)

    # Produit
    resp = await sim.send_message(session, "Le canapé SCANDINAVE", conversation_history)
    sim.print_message("user", "Le canapé SCANDINAVE")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "Le canapé SCANDINAVE"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})
    await asyncio.sleep(0.5)

    # Commande
    resp = await sim.send_message(session, "CMD-2024-22222", conversation_history)
    sim.print_message("user", "CMD-2024-22222")
    sim.print_message("assistant", resp["response"], resp["latency"])
    conversation_history.append({"role": "user", "content": "CMD-2024-22222"})
    conversation_history.append({"role": "assistant", "content": resp["response"]})

    if "Je récapitule" in resp["response"]:
        print("\n  ✅ Récapitulatif avec problème synthétisé!")
        if "grince" in resp["response"].lower():
            print("  ✅ Le bot a bien synthétisé le problème complexe!")
        await asyncio.sleep(0.5)

        resp = await sim.send_message(session, "Oui c'est correct", conversation_history)
        sim.print_message("user", "Oui c'est correct")
        sim.print_message("assistant", resp["response"], resp["latency"])
        success = resp["action"] == "create_ticket"
    else:
        success = False

    sim.end_time = time.time()
    sim.print_summary()

    return success


async def main():
    """Exécute tous les scénarios de test"""
    print("="*70)
    print("🎯 TESTS AVANCÉS DU MODE VOCAL")
    print("="*70)
    print(f"Début des tests: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    async with aiohttp.ClientSession() as session:
        results = {}

        # Scénario 1
        results["scenario_1"] = await scenario_1_tout_dun_coup(session)

        # Scénario 2
        results["scenario_2"] = await scenario_2_langage_familier(session)

        # Scénario 3
        results["scenario_3"] = await scenario_3_client_impatient(session)

        # Scénario 4
        results["scenario_4"] = await scenario_4_numero_en_premier(session)

        # Scénario 5
        results["scenario_5"] = await scenario_5_probleme_complexe(session)

    # Résumé final
    print("="*70)
    print("📊 RÉSUMÉ FINAL DES TESTS AVANCÉS")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for i, (scenario, success) in enumerate(results.items(), 1):
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"Scénario {i}: {status}")

    print(f"\n✅ Scénarios réussis: {passed}/{total}")

    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS! La communication fonctionne parfaitement!")
    elif passed >= total * 0.8:
        print(f"\n✅ Bon résultat: {passed}/{total} tests passés")
    else:
        print(f"\n⚠️  Certains tests ont échoué. Voir les détails ci-dessus.")

    print(f"\nFin des tests: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
