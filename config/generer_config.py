#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Générateur de Configuration depuis Formulaire Client
========================================================
Lit le formulaire client (FORMULAIRE_CLIENT.txt) et génère automatiquement
les fichiers chatbot_config.yaml et dashboard_config.yaml

Usage:
    python config/generer_config.py
"""

import yaml
import sys
import io
from pathlib import Path
from typing import Dict, Any

# Fix encoding for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Couleurs pour affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def print_header(msg: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def parse_formulaire(filepath: Path) -> Dict[str, str]:
    """Parse le formulaire client et retourne un dictionnaire de config"""
    config = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Ignorer commentaires et lignes vides
            if not line or line.startswith('#'):
                continue

            # Parser ligne: KEY = value
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                config[key] = value

    return config


def convert_oui_non_to_bool(value: str) -> bool:
    """Convertit 'oui'/'non' en boolean"""
    return value.lower() in ['oui', 'yes', 'true', '1']


def generate_chatbot_config(form: Dict[str, str]) -> Dict[str, Any]:
    """Génère la configuration chatbot depuis le formulaire"""

    # Déterminer les paramètres selon le budget
    if form.get('BUDGET_IA', 'faible') == 'faible':
        max_tokens = 300
        history_limit = 4
    elif form.get('BUDGET_IA') == 'moyen':
        max_tokens = 500
        history_limit = 6
    else:  # élevé
        max_tokens = 800
        history_limit = 10

    # Longueur réponses
    if form.get('LONGUEUR_REPONSES') == 'courte':
        max_tokens = 300
    elif form.get('LONGUEUR_REPONSES') == 'moyenne':
        max_tokens = 500
    else:  # longue
        max_tokens = 800

    # Construire la config
    config = {
        'company': {
            'name': form.get('ENTREPRISE_NOM', 'Mobilier de France'),
            'short_name': form.get('ENTREPRISE_SIGLE', 'MDF'),
            'support_email': form.get('ENTREPRISE_EMAIL_SAV', 'sav@example.fr'),
            'support_phone': form.get('ENTREPRISE_TELEPHONE', '+33 1 23 45 67 89'),
            'website': form.get('ENTREPRISE_SITE_WEB', 'https://www.example.fr')
        },

        'branding': {
            'primary_color': form.get('COULEUR_PRINCIPALE', '#DC2626'),
            'secondary_color': form.get('COULEUR_SECONDAIRE', '#F97316'),
            'accent_color': form.get('COULEUR_ACCENT', '#3B82F6'),
            'bot_avatar': form.get('ENTREPRISE_SIGLE', 'M')[0],
            'show_company_logo': True
        },

        'messages': {
            'welcome': {
                'fr': form.get('MESSAGE_ACCUEIL_FR', 'Bonjour !'),
                'en': form.get('MESSAGE_ACCUEIL_EN', 'Hello!'),
                'ar': form.get('MESSAGE_ACCUEIL_AR', 'مرحباً!')
            },
            'request_photos': {
                'fr': "📸 Avez-vous des photos du problème pour que je puisse mieux vous aider ?",
                'en': "📸 Do you have photos of the problem so I can better assist you?",
                'ar': "📸 هل لديك صور للمشكلة حتى أتمكن من مساعدتك بشكل أفضل؟"
            },
            'technical_error': {
                'fr': "Désolé, j'ai rencontré un problème technique. Pouvez-vous réessayer ?",
                'en': "Sorry, I encountered a technical problem. Can you try again?",
                'ar': "عذراً، واجهت مشكلة تقنية. هل يمكنك المحاولة مرة أخرى؟"
            }
        },

        'ai': {
            'model': form.get('MODELE_IA', 'gpt-3.5-turbo'),
            'temperature': 0.7,
            'max_tokens': max_tokens,
            'history_limit': history_limit
        },

        'detection': {
            'sav_keywords': [
                "problème", "probleme", "défaut", "defaut", "cassé", "casse",
                "déchirure", "dechirure", "livraison", "retard",
                "garantie", "sav", "retour", "réclamation", "reclamation",
                "commande", "cmd-", "pied", "abimé", "abime",
                "problem", "defect", "broken", "tear", "delivery", "warranty"
            ],
            'shopping_keywords': [
                "cherche", "besoin", "acheter", "canapé", "canape", "table", "meuble",
                "looking for", "need", "buy", "sofa", "furniture", "price"
            ]
        },

        'priorities': {
            'P0': {
                'label': "Critique",
                'color': "#DC2626",
                'sla_hours': int(form.get('SLA_P0_HEURES', 4)),
                'keywords': ["cassé", "rupture", "danger", "inutilisable"]
            },
            'P1': {
                'label': "Urgent",
                'color': "#F97316",
                'sla_hours': int(form.get('SLA_P1_HEURES', 24)),
                'keywords': ["déchirure", "défaut important", "ne fonctionne pas"]
            },
            'P2': {
                'label': "Normal",
                'color': "#FBBF24",
                'sla_hours': int(form.get('SLA_P2_HEURES', 48)),
                'keywords': ["défaut mineur", "petit", "grince"]
            },
            'P3': {
                'label': "Faible",
                'color': "#10B981",
                'sla_hours': int(form.get('SLA_P3_HEURES', 72)),
                'keywords': ["question", "information", "conseil"]
            }
        },

        'warranty': {
            'structure': {
                'duration_years': int(form.get('GARANTIE_STRUCTURE_ANNEES', 5)),
                'exclusions': ["Dommages dus à une mauvaise utilisation", "Usure normale"]
            },
            'fabric': {
                'duration_years': int(form.get('GARANTIE_TISSU_ANNEES', 2)),
                'exclusions': ["Taches", "Déchirures", "Brûlures", "Usure normale"]
            },
            'mechanisms': {
                'duration_years': int(form.get('GARANTIE_MECANISMES_ANNEES', 3)),
                'exclusions': ["Dommages dus à une surcharge", "Usure normale"]
            },
            'cushions': {
                'duration_years': int(form.get('GARANTIE_COUSSINS_ANNEES', 2)),
                'exclusions': ["Affaissement naturel", "Usure normale"]
            }
        },

        'upload': {
            'max_file_size_mb': int(form.get('TAILLE_MAX_FICHIER_MB', 10)),
            'max_files_per_request': int(form.get('NOMBRE_MAX_FICHIERS', 10)),
            'allowed_extensions': {
                'images': ["jpg", "jpeg", "png", "gif", "webp"],
                'videos': ["mp4", "mov", "avi", "webm"]
            }
        },

        'rate_limit': {
            'messages_per_minute': 20,
            'uploads_per_hour': 50
        },

        'voice': {
            'speech_enabled': convert_oui_non_to_bool(form.get('VOIX_SYNTHESE', 'oui')),
            'voice_input_enabled': convert_oui_non_to_bool(form.get('VOIX_RECONNAISSANCE', 'oui')),
            'default_voice_language': form.get('VOIX_LANGUE', 'fr-FR')
        },

        'notifications': {
            'send_email_on_ticket_creation': convert_oui_non_to_bool(form.get('NOTIFICATION_EMAIL', 'oui')),
            'send_sms_for_urgent_tickets': convert_oui_non_to_bool(form.get('NOTIFICATION_SMS', 'non')),
            'sav_team_email': form.get('EMAIL_EQUIPE_SAV', 'equipe-sav@example.fr')
        },

        'analytics': {
            'log_level': "INFO",
            'keep_conversation_history': True,
            'history_retention_days': 90
        }
    }

    # Ajouter mots-clés supplémentaires
    if form.get('MOTS_CLES_SAV_SUPPLEMENTAIRES'):
        extra_keywords = [k.strip() for k in form['MOTS_CLES_SAV_SUPPLEMENTAIRES'].split(',')]
        config['detection']['sav_keywords'].extend(extra_keywords)

    if form.get('MOTS_CLES_SHOPPING_SUPPLEMENTAIRES'):
        extra_keywords = [k.strip() for k in form['MOTS_CLES_SHOPPING_SUPPLEMENTAIRES'].split(',')]
        config['detection']['shopping_keywords'].extend(extra_keywords)

    return config


def generate_dashboard_config(form: Dict[str, str]) -> Dict[str, Any]:
    """Génère la configuration dashboard depuis le formulaire"""

    # Parser les colonnes
    colonnes = [c.strip() for c in form.get('DASHBOARD_COLONNES', 'ticket_id,customer,problem,priority,status,date').split(',')]

    config = {
        'appearance': {
            'title': form.get('DASHBOARD_TITRE', 'Tableau de Bord SAV'),
            'subtitle': form.get('DASHBOARD_SOUS_TITRE', 'Gestion centralisée des réclamations clients'),
            'theme': {
                'primary': form.get('COULEUR_PRINCIPALE', '#DC2626'),
                'secondary': form.get('COULEUR_SECONDAIRE', '#F97316'),
                'success': "#10B981",
                'warning': "#FBBF24",
                'danger': "#EF4444",
                'info': "#3B82F6"
            },
            'show_logo': True,
            'dark_mode_default': False
        },

        'statistics': {
            'total_tickets': {'enabled': True, 'label': "Total Tickets", 'icon': "📊", 'color': "#3B82F6"},
            'critical_tickets': {'enabled': True, 'label': "Critiques (P0)", 'icon': "🔴", 'color': "#DC2626"},
            'urgent_tickets': {'enabled': True, 'label': "Urgents (P1)", 'icon': "🟠", 'color': "#F97316"},
            'auto_resolved': {'enabled': True, 'label': "Auto-résolus", 'icon': "✅", 'color': "#10B981"}
        },

        'filters': {
            'priority': {'enabled': True, 'label': "Priorité:", 'default': "all"},
            'status': {'enabled': True, 'label': "Statut:", 'default': "all"},
            'date_range': {'enabled': True, 'label': "Période:", 'default': "last_7_days"}
        },

        'columns': {
            'order': colonnes,
            'ticket_id': {'enabled': 'ticket_id' in colonnes, 'label': "TICKET", 'width': "120px", 'sortable': True},
            'customer': {'enabled': 'customer' in colonnes, 'label': "CLIENT", 'width': "150px", 'sortable': True},
            'problem': {'enabled': 'problem' in colonnes, 'label': "PROBLÈME", 'width': "250px", 'sortable': False, 'max_chars': 50},
            'priority': {'enabled': 'priority' in colonnes, 'label': "PRIORITÉ", 'width': "100px", 'sortable': True, 'show_badge': True},
            'tone': {'enabled': 'tone' in colonnes, 'label': "TON", 'width': "100px", 'sortable': True, 'show_emoji': True},
            'status': {'enabled': 'status' in colonnes, 'label': "STATUT", 'width': "150px", 'sortable': True, 'show_badge': True},
            'date': {'enabled': 'date' in colonnes, 'label': "DATE", 'width': "120px", 'sortable': True, 'format': "relative"},
            'actions': {'enabled': True, 'label': "ACTIONS", 'width': "100px"}
        },

        'actions': {
            'view_details': {'enabled': True, 'icon': "👁️", 'color': "#3B82F6", 'tooltip': "Voir le dossier complet"},
            'edit': {'enabled': False},
            'delete': {'enabled': False},
            'mark_resolved': {'enabled': False}
        },

        'modal': {
            'width': "90%",
            'max_width': "1200px",
            'sections': [
                "ticket_info", "client_info", "product_info", "problem_description",
                "tone_analysis", "warranty_check", "photos_videos", "sla",
                "resolution", "client_summary", "action_history"
            ]
        },

        'statuses': {
            'pending': {'label': "En attente", 'color': "#FBBF24", 'icon': "⏳"},
            'in_progress': {'label': "En cours", 'color': "#3B82F6", 'icon': "🔄"},
            'escalated_to_human': {'label': "Escaladé", 'color': "#F97316", 'icon': "⬆️"},
            'resolved': {'label': "Résolu", 'color': "#10B981", 'icon': "✅"},
            'closed': {'label': "Fermé", 'color': "#6B7280", 'icon': "🔒"}
        },

        'notifications': {
            'auto_refresh': {
                'enabled': True,
                'interval_seconds': int(form.get('DASHBOARD_REFRESH_SECONDES', 30))
            },
            'sound_alerts': {'enabled': False},
            'browser_notifications': {'enabled': False},
            'tab_badge': {'enabled': True}
        },

        'export': {
            'enabled': convert_oui_non_to_bool(form.get('DASHBOARD_EXPORT', 'non')),
            'formats': ["csv", "excel", "pdf"] if convert_oui_non_to_bool(form.get('DASHBOARD_EXPORT', 'non')) else []
        },

        'responsive': {
            'mobile_breakpoint': 768,
            'mobile_columns': ["ticket_id", "priority", "status", "actions"],
            'tablet_columns': ["ticket_id", "customer", "priority", "status", "date", "actions"]
        }
    }

    return config


def main():
    """Point d'entrée principal"""
    print_header("🔧 GÉNÉRATEUR DE CONFIGURATION DEPUIS FORMULAIRE")

    # Chemins
    config_dir = Path(__file__).parent
    formulaire_path = config_dir / "FORMULAIRE_CLIENT.txt"
    chatbot_config_path = config_dir / "chatbot_config.yaml"
    dashboard_config_path = config_dir / "dashboard_config.yaml"

    # Backup des configs existantes
    backup_dir = config_dir / "backup"
    backup_dir.mkdir(exist_ok=True)

    if chatbot_config_path.exists():
        import shutil
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy(chatbot_config_path, backup_dir / f"chatbot_config_{timestamp}.yaml")
        print_info(f"Backup créé: backup/chatbot_config_{timestamp}.yaml")

    if dashboard_config_path.exists():
        import shutil
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy(dashboard_config_path, backup_dir / f"dashboard_config_{timestamp}.yaml")
        print_info(f"Backup créé: backup/dashboard_config_{timestamp}.yaml")

    # Parser le formulaire
    print_header("📝 Lecture du formulaire client")

    if not formulaire_path.exists():
        print_error(f"Fichier formulaire introuvable: {formulaire_path}")
        return 1

    try:
        form_data = parse_formulaire(formulaire_path)
        print_success(f"{len(form_data)} paramètres lus depuis le formulaire")
    except Exception as e:
        print_error(f"Erreur lors de la lecture du formulaire: {e}")
        return 1

    # Générer chatbot_config.yaml
    print_header("🤖 Génération chatbot_config.yaml")
    try:
        chatbot_config = generate_chatbot_config(form_data)

        with open(chatbot_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(chatbot_config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        print_success(f"Fichier généré: {chatbot_config_path}")
        print_info(f"  - Entreprise: {chatbot_config['company']['name']}")
        print_info(f"  - Modèle IA: {chatbot_config['ai']['model']}")
        print_info(f"  - SLA P0: {chatbot_config['priorities']['P0']['sla_hours']}h")
    except Exception as e:
        print_error(f"Erreur génération chatbot_config: {e}")
        return 1

    # Générer dashboard_config.yaml
    print_header("📊 Génération dashboard_config.yaml")
    try:
        dashboard_config = generate_dashboard_config(form_data)

        with open(dashboard_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(dashboard_config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        print_success(f"Fichier généré: {dashboard_config_path}")
        print_info(f"  - Titre: {dashboard_config['appearance']['title']}")
        print_info(f"  - Couleur: {dashboard_config['appearance']['theme']['primary']}")
        print_info(f"  - Colonnes: {len(dashboard_config['columns']['order'])}")
    except Exception as e:
        print_error(f"Erreur génération dashboard_config: {e}")
        return 1

    # Résumé
    print_header("✅ GÉNÉRATION TERMINÉE")
    print_success("Les configurations ont été générées avec succès !")
    print_info("")
    print_info("Prochaines étapes:")
    print_info("  1. Vérifier les fichiers générés")
    print_info("  2. Valider: python config/validate_config.py")
    print_info("  3. Appliquer: docker-compose restart")
    print_info("")
    print_info(f"💾 Backups sauvegardés dans: {backup_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
