#!/usr/bin/env python3
"""
Script de test automatisé pour le mode vocal
Simule plusieurs conversations complètes avec différents scénarios
"""
import asyncio
import aiohttp
import json
import time
from typing import List, Dict
from datetime import datetime
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
        self.conversation_history = []
        self.session_id = f"test_{int(time.time())}"
        self.start_time = None
        self.end_time = None
        self.latencies = []

    async def send_message(self, session: aiohttp.ClientSession, message: str) -> dict:
        """Envoie un message et retourne la réponse"""
        start = time.time()

        async with session.post(
            f"{API_URL}/api/voice/chat",
            json={
                "message": message,
                "conversation_history": self.conversation_history,
                "session_id": self.session_id
            }
        ) as response:
            if response.status != 200:
                raise Exception(f"Erreur API: {response.status}")

            data = await response.json()
            latency = time.time() - start
            self.latencies.append(latency)

            # Ajouter à l'historique
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": data["response"]})

            return {
                "response": data["response"],
                "action": data.get("action"),
                "ticket_data": data.get("ticket_data"),
                "latency": latency
            }

    def print_message(self, role: str, content: str, latency: float = None):
        """Affiche un message formaté"""
        icon = "👤" if role == "user" else "🤖"
        latency_info = f" ({latency:.2f}s)" if latency else ""
        print(f"  {icon} {role.upper()}{latency_info}: {content}")

    def print_summary(self):
        """Affiche un résumé de la conversation"""
        duration = self.end_time - self.start_time if self.end_time else 0
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0

        print(f"\n📊 RÉSUMÉ - {self.scenario_name}")
        print(f"  • Durée totale: {duration:.2f}s")
        print(f"  • Nombre d'échanges: {len(self.conversation_history) // 2}")
        print(f"  • Latence moyenne: {avg_latency:.2f}s")
        print(f"  • Latence min: {min(self.latencies):.2f}s" if self.latencies else "")
        print(f"  • Latence max: {max(self.latencies):.2f}s" if self.latencies else "")


# ==================== SCÉNARIOS DE TEST ====================

async def scenario_1_conversation_parfaite(session: aiohttp.ClientSession):
    """
    Scénario 1: Conversation parfaite - Client coopératif
    Marie Dupont, canapé OSLO avec pied cassé
    """
    print("\n" + "="*70)
    print("🧪 SCÉNARIO 1: Conversation parfaite - Client coopératif")
    print("="*70)

    sim = ConversationSimulator("Scénario 1")
    sim.start_time = time.time()

    # Étape 1: Nom
    resp = await sim.send_message(session, "Bonjour, je m'appelle Marie Dupont")
    sim.print_message("user", "Bonjour, je m'appelle Marie Dupont")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.5)

    # Étape 2: Problème
    resp = await sim.send_message(session, "Mon canapé a un pied cassé")
    sim.print_message("user", "Mon canapé a un pied cassé")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.5)

    # Étape 3: Produit
    resp = await sim.send_message(session, "C'est le modèle OSLO")
    sim.print_message("user", "C'est le modèle OSLO")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.5)

    # Étape 4: Numéro de commande
    resp = await sim.send_message(session, "CMD-2024-12345")
    sim.print_message("user", "CMD-2024-12345")
    sim.print_message("assistant", resp["response"], resp["latency"])

    # Vérifier le récapitulatif
    if "Je récapitule" in resp["response"]:
        print("\n  ✅ Récapitulatif détecté!")

    await asyncio.sleep(0.5)

    # Étape 5: Confirmation
    resp = await sim.send_message(session, "Oui")
    sim.print_message("user", "Oui")
    sim.print_message("assistant", resp["response"], resp["latency"])

    # Vérifier la création du ticket
    if resp["action"] == "create_ticket":
        print("\n  ✅ Action create_ticket détectée!")
        print(f"  📋 Données extraites:")
        for key, value in resp["ticket_data"].items():
            print(f"     • {key}: {value}")

    sim.end_time = time.time()
    sim.print_summary()

    return resp["ticket_data"] is not None


async def scenario_2_client_verbose(session: aiohttp.ClientSession):
    """
    Scénario 2: Client très bavard
    Jean Martin, table NORDIC rayée, donne trop de détails
    """
    print("\n" + "="*70)
    print("🧪 SCÉNARIO 2: Client très bavard - Trop de détails")
    print("="*70)

    sim = ConversationSimulator("Scénario 2")
    sim.start_time = time.time()

    # Étape 1: Nom avec beaucoup de détails
    resp = await sim.send_message(session,
        "Bonjour, je m'appelle Jean Martin, j'habite à Paris dans le 15ème arrondissement")
    sim.print_message("user", "Bonjour, je m'appelle Jean Martin, j'habite à Paris...")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.5)

    # Étape 2: Problème avec BEAUCOUP de détails
    resp = await sim.send_message(session,
        "Alors voilà, j'ai acheté une table il y a 3 mois et j'ai remarqué hier en nettoyant qu'il y avait une rayure assez profonde sur le dessus, je ne sais pas comment c'est arrivé, peut-être que c'est mon chat")
    sim.print_message("user", "Alors voilà, j'ai acheté une table il y a 3 mois...")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.5)

    # Étape 3: Produit
    resp = await sim.send_message(session, "C'est le modèle NORDIC en chêne massif")
    sim.print_message("user", "C'est le modèle NORDIC en chêne massif")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.5)

    # Étape 4: Numéro de commande
    resp = await sim.send_message(session, "CMD-2024-98765")
    sim.print_message("user", "CMD-2024-98765")
    sim.print_message("assistant", resp["response"], resp["latency"])

    # Vérifier que le bot a bien synthétisé le problème
    if "Je récapitule" in resp["response"]:
        print("\n  ✅ Récapitulatif détecté!")
        if "rayure" in resp["response"].lower() or "rayé" in resp["response"].lower():
            print("  ✅ Le bot a bien synthétisé le problème (rayure)")

    await asyncio.sleep(0.5)

    # Étape 5: Confirmation
    resp = await sim.send_message(session, "D'accord")
    sim.print_message("user", "D'accord")
    sim.print_message("assistant", resp["response"], resp["latency"])

    sim.end_time = time.time()
    sim.print_summary()

    return resp["action"] == "create_ticket"


async def scenario_3_client_confus(session: aiohttp.ClientSession):
    """
    Scénario 3: Client confus qui mélange les informations
    Sophie Leblanc, fauteuil COMFORT, donne des infos dans le désordre
    """
    print("\n" + "="*70)
    print("🧪 SCÉNARIO 3: Client confus - Informations dans le désordre")
    print("="*70)

    sim = ConversationSimulator("Scénario 3")
    sim.start_time = time.time()

    # Le client donne le numéro de commande dans sa première réponse
    resp = await sim.send_message(session,
        "Bonjour, c'est Sophie Leblanc, ma commande c'est CMD-2024-55555")
    sim.print_message("user", "Bonjour, c'est Sophie Leblanc, commande CMD-2024-55555")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.5)

    # Le client donne le produit avant le problème
    resp = await sim.send_message(session,
        "C'est pour mon fauteuil COMFORT")
    sim.print_message("user", "C'est pour mon fauteuil COMFORT")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.5)

    # Enfin le problème
    resp = await sim.send_message(session,
        "Le tissu se déchire sur l'accoudoir droit")
    sim.print_message("user", "Le tissu se déchire sur l'accoudoir droit")
    sim.print_message("assistant", resp["response"], resp["latency"])

    # Le bot demande confirmation du numéro de commande (qu'il a déjà)
    # mais devrait faire le récapitulatif
    await asyncio.sleep(0.5)

    # Le client confirme
    resp = await sim.send_message(session, "Oui c'est ça")
    sim.print_message("user", "Oui c'est ça")
    sim.print_message("assistant", resp["response"], resp["latency"])

    # Vérifier le récapitulatif
    if "Je récapitule" in resp["response"]:
        print("\n  ✅ Le bot a réussi à réorganiser les informations!")

    await asyncio.sleep(0.5)

    # Confirmation finale pour créer le ticket
    resp = await sim.send_message(session, "Oui")
    sim.print_message("user", "Oui")
    sim.print_message("assistant", resp["response"], resp["latency"])

    sim.end_time = time.time()
    sim.print_summary()

    return resp["action"] == "create_ticket"


async def scenario_4_client_hesite(session: aiohttp.ClientSession):
    """
    Scénario 4: Client qui hésite et se corrige
    Pierre Dubois, lit SERENITY, se trompe de numéro de commande
    """
    print("\n" + "="*70)
    print("🧪 SCÉNARIO 4: Client qui hésite et se corrige")
    print("="*70)

    sim = ConversationSimulator("Scénario 4")
    sim.start_time = time.time()

    # Nom
    resp = await sim.send_message(session, "Pierre Dubois")
    sim.print_message("user", "Pierre Dubois")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.5)

    # Problème
    resp = await sim.send_message(session, "Mon lit grince beaucoup")
    sim.print_message("user", "Mon lit grince beaucoup")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.5)

    # Produit
    resp = await sim.send_message(session, "Le lit SERENITY")
    sim.print_message("user", "Le lit SERENITY")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.5)

    # Numéro de commande (se trompe d'abord)
    resp = await sim.send_message(session, "Euh... CMD-2024-11111")
    sim.print_message("user", "Euh... CMD-2024-11111")
    sim.print_message("assistant", resp["response"], resp["latency"])

    # Récapitulatif
    if "Je récapitule" in resp["response"]:
        print("\n  ℹ️  Récapitulatif avec mauvais numéro")

    await asyncio.sleep(0.5)

    # Le client se rend compte de son erreur
    resp = await sim.send_message(session,
        "Non attendez, je me suis trompé, c'est CMD-2024-77777")
    sim.print_message("user", "Non attendez, je me suis trompé, c'est CMD-2024-77777")
    sim.print_message("assistant", resp["response"], resp["latency"])

    await asyncio.sleep(0.5)

    # Le bot devrait redemander la commande
    resp = await sim.send_message(session, "CMD-2024-77777")
    sim.print_message("user", "CMD-2024-77777")
    sim.print_message("assistant", resp["response"], resp["latency"])

    # Nouveau récapitulatif
    if "Je récapitule" in resp["response"] and "77777" in resp["response"]:
        print("\n  ✅ Le bot a bien pris en compte la correction!")

    await asyncio.sleep(0.5)

    # Confirmation
    resp = await sim.send_message(session, "Oui cette fois c'est bon")
    sim.print_message("user", "Oui cette fois c'est bon")
    sim.print_message("assistant", resp["response"], resp["latency"])

    sim.end_time = time.time()
    sim.print_summary()

    return resp["action"] == "create_ticket"


async def scenario_5_client_presse(session: aiohttp.ClientSession):
    """
    Scénario 5: Client pressé - Réponses ultra courtes
    Luc Bernard, armoire CLASSIC, portes mal alignées
    """
    print("\n" + "="*70)
    print("🧪 SCÉNARIO 5: Client pressé - Réponses très courtes")
    print("="*70)

    sim = ConversationSimulator("Scénario 5")
    sim.start_time = time.time()

    # Réponses ultra courtes
    resp = await sim.send_message(session, "Luc Bernard")
    sim.print_message("user", "Luc Bernard")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.3)  # Délai court car pressé

    resp = await sim.send_message(session, "Portes mal alignées")
    sim.print_message("user", "Portes mal alignées")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.3)

    resp = await sim.send_message(session, "Armoire CLASSIC")
    sim.print_message("user", "Armoire CLASSIC")
    sim.print_message("assistant", resp["response"], resp["latency"])
    await asyncio.sleep(0.3)

    resp = await sim.send_message(session, "CMD-2024-33333")
    sim.print_message("user", "CMD-2024-33333")
    sim.print_message("assistant", resp["response"], resp["latency"])

    if "Je récapitule" in resp["response"]:
        print("\n  ✅ Le bot a géré les réponses courtes!")

    await asyncio.sleep(0.3)

    resp = await sim.send_message(session, "OK")
    sim.print_message("user", "OK")
    sim.print_message("assistant", resp["response"], resp["latency"])

    sim.end_time = time.time()
    sim.print_summary()

    return resp["action"] == "create_ticket"


async def test_extraction_donnees():
    """Test de la fonction d'extraction de données"""
    print("\n" + "="*70)
    print("🧪 TEST: Extraction des données du récapitulatif")
    print("="*70)

    from backend.app.api.endpoints.voice import extract_ticket_data_from_recap

    recap_examples = [
        {
            "name": "Format standard",
            "text": """Parfait ! Je récapitule:
Nom: Marie Dupont
Problème: Pied de canapé cassé
Produit: Canapé OSLO
Commande: CMD-2024-12345

Si ces informations sont correctes, dites OUI pour créer votre ticket SAV.""",
            "expected": {
                "customer_name": "Marie Dupont",
                "problem_description": "Pied de canapé cassé",
                "product": "Canapé OSLO",
                "order_number": "CMD-2024-12345"
            }
        },
        {
            "name": "Avec majuscules",
            "text": """Je récapitule:
NOM: Jean Martin
PROBLÈME: Table rayée
PRODUIT: Table NORDIC
COMMANDE: CMD-2024-98765""",
            "expected": {
                "customer_name": "Jean Martin",
                "problem_description": "Table rayée",
                "product": "Table NORDIC",
                "order_number": "CMD-2024-98765"
            }
        }
    ]

    all_pass = True
    for example in recap_examples:
        print(f"\n  Test: {example['name']}")
        result = extract_ticket_data_from_recap(example["text"])

        for key, expected_value in example["expected"].items():
            if result[key] == expected_value:
                print(f"    ✅ {key}: {result[key]}")
            else:
                print(f"    ❌ {key}: attendu '{expected_value}', obtenu '{result[key]}'")
                all_pass = False

    return all_pass


async def main():
    """Fonction principale de test"""
    print("\n" + "="*70)
    print("🎯 TESTS AUTOMATISÉS DU MODE VOCAL")
    print("="*70)
    print(f"Début des tests: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "scenarios_passed": 0,
        "scenarios_failed": 0,
        "test_extraction": False
    }

    async with aiohttp.ClientSession() as session:
        # Test 1: Conversation parfaite
        try:
            success = await scenario_1_conversation_parfaite(session)
            if success:
                results["scenarios_passed"] += 1
                print("\n✅ Scénario 1: RÉUSSI")
            else:
                results["scenarios_failed"] += 1
                print("\n❌ Scénario 1: ÉCHOUÉ")
        except Exception as e:
            print(f"\n❌ Scénario 1: ERREUR - {e}")
            results["scenarios_failed"] += 1

        await asyncio.sleep(2)

        # Test 2: Client verbose
        try:
            success = await scenario_2_client_verbose(session)
            if success:
                results["scenarios_passed"] += 1
                print("\n✅ Scénario 2: RÉUSSI")
            else:
                results["scenarios_failed"] += 1
                print("\n❌ Scénario 2: ÉCHOUÉ")
        except Exception as e:
            print(f"\n❌ Scénario 2: ERREUR - {e}")
            results["scenarios_failed"] += 1

        await asyncio.sleep(2)

        # Test 3: Client confus
        try:
            success = await scenario_3_client_confus(session)
            if success:
                results["scenarios_passed"] += 1
                print("\n✅ Scénario 3: RÉUSSI")
            else:
                results["scenarios_failed"] += 1
                print("\n❌ Scénario 3: ÉCHOUÉ")
        except Exception as e:
            print(f"\n❌ Scénario 3: ERREUR - {e}")
            results["scenarios_failed"] += 1

        await asyncio.sleep(2)

        # Test 4: Client qui se corrige
        try:
            success = await scenario_4_client_hesite(session)
            if success:
                results["scenarios_passed"] += 1
                print("\n✅ Scénario 4: RÉUSSI")
            else:
                results["scenarios_failed"] += 1
                print("\n❌ Scénario 4: ÉCHOUÉ")
        except Exception as e:
            print(f"\n❌ Scénario 4: ERREUR - {e}")
            results["scenarios_failed"] += 1

        await asyncio.sleep(2)

        # Test 5: Client pressé
        try:
            success = await scenario_5_client_presse(session)
            if success:
                results["scenarios_passed"] += 1
                print("\n✅ Scénario 5: RÉUSSI")
            else:
                results["scenarios_failed"] += 1
                print("\n❌ Scénario 5: ÉCHOUÉ")
        except Exception as e:
            print(f"\n❌ Scénario 5: ERREUR - {e}")
            results["scenarios_failed"] += 1

    # Test d'extraction
    try:
        results["test_extraction"] = await test_extraction_donnees()
        if results["test_extraction"]:
            print("\n✅ Test extraction: RÉUSSI")
        else:
            print("\n❌ Test extraction: ÉCHOUÉ")
    except Exception as e:
        print(f"\n❌ Test extraction: ERREUR - {e}")

    # Résumé final
    print("\n" + "="*70)
    print("📊 RÉSUMÉ FINAL DES TESTS")
    print("="*70)
    print(f"✅ Scénarios réussis: {results['scenarios_passed']}/5")
    print(f"❌ Scénarios échoués: {results['scenarios_failed']}/5")
    print(f"{'✅' if results['test_extraction'] else '❌'} Test extraction: {'RÉUSSI' if results['test_extraction'] else 'ÉCHOUÉ'}")

    total_success = results["scenarios_passed"] == 5 and results["test_extraction"]
    if total_success:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
    else:
        print("\n⚠️  Certains tests ont échoué. Voir les détails ci-dessus.")

    print(f"\nFin des tests: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
