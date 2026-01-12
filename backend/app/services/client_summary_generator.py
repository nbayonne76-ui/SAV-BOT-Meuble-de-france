# -*- coding: utf-8 -*-
# backend/app/services/client_summary_generator.py
"""
Générateur de récapitulatif client pour validation
Crée un bilan clair et concis à envoyer par email/SMS
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ClientSummary:
    """Récapitulatif client structuré"""
    summary_id: str
    ticket_id: str
    client_name: str
    order_number: str
    product_name: str
    problem_summary: str
    warranty_status: str
    priority: str
    next_steps: str
    response_deadline: str
    validation_required: bool
    validation_link: Optional[str] = None
    email_body: str = ""
    sms_body: str = ""


class ClientSummaryGenerator:
    """
    Génère des récapitulatifs clients professionnels
    pour validation et traçabilité
    """

    def generate_summary(
        self,
        ticket_data: Dict,
        client_data: Dict,
        tone_analysis: Optional[Dict] = None
    ) -> ClientSummary:
        """
        Génère un récapitulatif client complet

        Args:
            ticket_data: Données du ticket SAV
            client_data: Données client
            tone_analysis: Analyse de ton (optionnel)

        Returns:
            ClientSummary avec email et SMS prêts à envoyer
        """

        summary_id = f"SUM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Données de base
        ticket_id = ticket_data.get("ticket_id", "N/A")
        client_name = client_data.get("name", "Client")
        order_number = client_data.get("order_number", "N/A")
        product_name = client_data.get("product", "Produit")
        problem_description = ticket_data.get("problem_description", "")

        # Résumé court du problème (max 100 caractères)
        problem_summary = self._summarize_problem(
            problem_description,
            ticket_data.get("problem_category", "")
        )

        # Statut garantie
        warranty_covered = ticket_data.get("warranty_covered", False)
        warranty_status = "✅ Sous garantie" if warranty_covered else "❌ Hors garantie"

        # Priorité
        priority_info = ticket_data.get("priority", {})
        priority = f"{priority_info.get('emoji', '')} {priority_info.get('label', 'MOYENNE')}"

        # Délai de réponse
        response_time = tone_analysis.get("recommended_response_time", "48h") if tone_analysis else "48h"
        response_deadline = self._calculate_deadline(response_time)

        # Prochaines étapes
        next_steps = self._generate_next_steps(ticket_data, warranty_covered)

        # Validation requise si non auto-résolu
        auto_resolved = ticket_data.get("auto_resolved", False)
        validation_required = not auto_resolved

        # Lien de validation (à générer par le frontend)
        validation_link = f"https://mobilierdefrance.com/sav/validate/{ticket_id}" if validation_required else None

        # Générer email
        email_body = self._generate_email(
            client_name=client_name,
            ticket_id=ticket_id,
            order_number=order_number,
            product_name=product_name,
            problem_summary=problem_summary,
            warranty_status=warranty_status,
            priority=priority,
            next_steps=next_steps,
            response_deadline=response_deadline,
            validation_link=validation_link,
            auto_resolved=auto_resolved
        )

        # Générer SMS
        sms_body = self._generate_sms(
            client_name=client_name,
            ticket_id=ticket_id,
            response_deadline=response_deadline,
            validation_link=validation_link
        )

        logger.info(f"📧 Récapitulatif généré: {summary_id} pour ticket {ticket_id}")

        return ClientSummary(
            summary_id=summary_id,
            ticket_id=ticket_id,
            client_name=client_name,
            order_number=order_number,
            product_name=product_name,
            problem_summary=problem_summary,
            warranty_status=warranty_status,
            priority=priority,
            next_steps=next_steps,
            response_deadline=response_deadline,
            validation_required=validation_required,
            validation_link=validation_link,
            email_body=email_body,
            sms_body=sms_body
        )

    def _summarize_problem(self, description: str, category: str) -> str:
        """Résume le problème en une phrase courte"""

        # Mapping catégorie → résumé
        category_labels = {
            "structural": "Problème de structure",
            "mechanism": "Dysfonctionnement mécanisme",
            "fabric": "Défaut tissu/cuir",
            "cushions": "Affaissement coussins",
            "delivery": "Dommage à la livraison",
            "assembly": "Problème de montage",
            "smell": "Odeur inhabituelle",
            "dimensions": "Problème de dimensions"
        }

        base_summary = category_labels.get(category, "Problème signalé")

        # Extraire le premier détail du message (max 50 caractères)
        if description:
            words = description.strip().split()[:10]
            detail = " ".join(words)
            if len(detail) > 50:
                detail = detail[:47] + "..."
            return f"{base_summary}: {detail}"

        return base_summary

    def _calculate_deadline(self, response_time: str) -> str:
        """Calcule la date limite de réponse"""

        hours_map = {
            "4h": 4,
            "24h": 24,
            "48h": 48,
            "72h": 72
        }

        hours = hours_map.get(response_time, 48)
        deadline = datetime.now()

        # Ajouter les heures
        from datetime import timedelta
        deadline += timedelta(hours=hours)

        return deadline.strftime("%d/%m/%Y à %Hh%M")

    def _generate_next_steps(self, ticket_data: Dict, warranty_covered: bool) -> str:
        """Génère les prochaines étapes selon le ticket"""

        status = ticket_data.get("status", "")
        resolution_type = ticket_data.get("resolution_type", "")

        if ticket_data.get("auto_resolved"):
            return "✅ Votre demande a été traitée automatiquement. Consultez la solution ci-dessous."

        elif status == "escalated_to_human":
            return "👤 Un conseiller SAV vous contactera rapidement pour étudier votre cas."

        elif status == "awaiting_technician":
            return "👷 Un technicien vous contactera pour planifier une intervention."

        elif status == "evidence_collection":
            return "📸 Veuillez fournir les photos/vidéos demandées pour traiter votre demande."

        elif not warranty_covered:
            return "ℹ️ Votre garantie est expirée. Nous vous proposerons des solutions alternatives (réparation payante, conseils)."

        else:
            return "📋 Votre demande est en cours de traitement. Nous revenons vers vous sous 48h."

    def _generate_email(
        self,
        client_name: str,
        ticket_id: str,
        order_number: str,
        product_name: str,
        problem_summary: str,
        warranty_status: str,
        priority: str,
        next_steps: str,
        response_deadline: str,
        validation_link: Optional[str],
        auto_resolved: bool
    ) -> str:
        """Génère le corps de l'email de confirmation"""

        email = f"""
Bonjour {client_name},

Nous avons bien reçu votre demande SAV et nous vous remercions de votre confiance.

═══════════════════════════════════════════════════════
📋 RÉCAPITULATIF DE VOTRE DEMANDE SAV
═══════════════════════════════════════════════════════

🎫 Numéro de ticket : {ticket_id}
📦 Commande : {order_number}
🛋️ Produit : {product_name}

⚠️ Problème signalé :
{problem_summary}

🛡️ Garantie : {warranty_status}
🎯 Priorité : {priority}

───────────────────────────────────────────────────────
📍 PROCHAINES ÉTAPES
───────────────────────────────────────────────────────

{next_steps}

⏰ Délai de réponse : Avant le {response_deadline}

"""

        # Ajouter validation si requise
        if validation_link and not auto_resolved:
            email += f"""
───────────────────────────────────────────────────────
✅ VALIDATION REQUISE
───────────────────────────────────────────────────────

Pour traiter votre demande, merci de valider les informations ci-dessus :

👉 {validation_link}

Cette validation nous permet de :
• Confirmer que vous êtes bien à l'origine de la demande
• Éviter tout malentendu sur les éléments fournis
• Accélérer le traitement de votre dossier

⚠️ Sans validation sous 72h, votre demande sera automatiquement annulée.

"""

        # Pied de page
        email += """
═══════════════════════════════════════════════════════

💡 CONSEILS :

• Conservez ce numéro de ticket : {ticket_id}
• Consultez l'état de votre demande : https://mobilierdefrance.com/sav/suivi
• Besoin d'aide ? Répondez à cet email ou appelez le 01 XX XX XX XX

───────────────────────────────────────────────────────

Cordialement,
L'équipe SAV Meuble de France

🌐 www.mobilierdefrance.com
📧 sav@mobilierdefrance.com
📞 01 XX XX XX XX (Lun-Ven 9h-18h)

═══════════════════════════════════════════════════════
""".replace("{ticket_id}", ticket_id)

        return email.strip()

    def _generate_sms(
        self,
        client_name: str,
        ticket_id: str,
        response_deadline: str,
        validation_link: Optional[str]
    ) -> str:
        """Génère le SMS de confirmation (max 160 caractères)"""

        if validation_link:
            sms = (
                f"Meuble de France - SAV {ticket_id} créé. "
                f"VALIDEZ votre demande : {validation_link} "
                f"Réponse avant le {response_deadline}"
            )
        else:
            sms = (
                f"Meuble de France - Votre demande SAV {ticket_id} est enregistrée. "
                f"Réponse avant le {response_deadline}. "
                f"Suivi: mobilierdefrance.com/sav"
            )

        return sms


# Instance globale
client_summary_generator = ClientSummaryGenerator()
