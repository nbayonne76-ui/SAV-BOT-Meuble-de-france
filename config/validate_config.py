#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validateur de Configuration SAV Bot
=====================================
Vérifie que les fichiers de configuration sont corrects avant déploiement.

Usage:
    python config/validate_config.py
"""

import yaml
import sys
import io
from pathlib import Path
from typing import Dict, List, Any

# Fix encoding for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Couleurs pour affichage terminal
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


def load_yaml(filepath: Path) -> Dict:
    """Charge et parse un fichier YAML"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print_error(f"Erreur de syntaxe YAML dans {filepath.name}: {e}")
        return None
    except FileNotFoundError:
        print_error(f"Fichier introuvable: {filepath}")
        return None


def validate_chatbot_config(config: Dict) -> List[str]:
    """Valide la configuration du chatbot"""
    errors = []

    # Vérifier sections obligatoires
    required_sections = [
        'company', 'branding', 'messages', 'ai',
        'detection', 'priorities', 'warranty', 'upload'
    ]

    for section in required_sections:
        if section not in config:
            errors.append(f"Section manquante: {section}")

    if 'company' in config:
        # Vérifier champs entreprise
        required_company = ['name', 'short_name', 'support_email']
        for field in required_company:
            if field not in config['company']:
                errors.append(f"Champ manquant: company.{field}")

    if 'ai' in config:
        # Vérifier modèle IA
        valid_models = ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
        model = config['ai'].get('model')
        if model not in valid_models:
            errors.append(f"Modèle IA invalide: {model}. Valeurs autorisées: {valid_models}")

        # Vérifier temperature
        temp = config['ai'].get('temperature', 0.7)
        if not 0.0 <= temp <= 1.0:
            errors.append(f"Temperature invalide: {temp}. Doit être entre 0.0 et 1.0")

        # Vérifier max_tokens
        max_tokens = config['ai'].get('max_tokens', 500)
        if not 1 <= max_tokens <= 4000:
            errors.append(f"max_tokens invalide: {max_tokens}. Doit être entre 1 et 4000")

    if 'priorities' in config:
        # Vérifier que P0, P1, P2, P3 existent
        for priority in ['P0', 'P1', 'P2', 'P3']:
            if priority not in config['priorities']:
                errors.append(f"Priorité manquante: {priority}")
            else:
                # Vérifier SLA
                if 'sla_hours' not in config['priorities'][priority]:
                    errors.append(f"SLA manquant pour {priority}")

    if 'upload' in config:
        # Vérifier taille max
        max_size = config['upload'].get('max_file_size_mb')
        if max_size and max_size > 100:
            print_warning(f"Taille max upload très élevée: {max_size}MB")

    return errors


def validate_dashboard_config(config: Dict) -> List[str]:
    """Valide la configuration du dashboard"""
    errors = []

    # Vérifier sections obligatoires
    required_sections = [
        'appearance', 'statistics', 'filters',
        'columns', 'actions', 'modal', 'statuses'
    ]

    for section in required_sections:
        if section not in config:
            errors.append(f"Section manquante: {section}")

    if 'appearance' in config and 'theme' in config['appearance']:
        # Vérifier format couleurs
        theme = config['appearance']['theme']
        for color_name, color_value in theme.items():
            if not color_value.startswith('#'):
                errors.append(f"Couleur invalide: {color_name} = {color_value}. Doit commencer par #")
            if len(color_value) not in [4, 7]:  # #RGB ou #RRGGBB
                errors.append(f"Format couleur invalide: {color_name} = {color_value}")

    if 'columns' in config:
        # Vérifier qu'au moins 3 colonnes sont activées
        enabled_cols = [
            col for col, settings in config['columns'].items()
            if isinstance(settings, dict) and settings.get('enabled', False)
        ]
        if len(enabled_cols) < 3:
            print_warning(f"Seulement {len(enabled_cols)} colonnes activées. Minimum recommandé: 3")

    if 'statuses' in config:
        # Vérifier statuts essentiels
        required_statuses = ['pending', 'resolved', 'escalated_to_human']
        for status in required_statuses:
            if status not in config['statuses']:
                errors.append(f"Statut manquant: {status}")

    return errors


def check_config_completeness(chatbot_cfg: Dict, dashboard_cfg: Dict) -> List[str]:
    """Vérifications croisées entre les deux configs"""
    warnings = []

    # Vérifier que les priorités sont cohérentes
    if 'priorities' in chatbot_cfg:
        chatbot_priorities = set(chatbot_cfg['priorities'].keys())
        # Vérifier que le dashboard peut gérer ces priorités
        # (pour l'instant juste un warning informatif)
        print_info(f"Priorités définies: {', '.join(chatbot_priorities)}")

    # Vérifier cohérence des couleurs
    if 'branding' in chatbot_cfg and 'appearance' in dashboard_cfg:
        chatbot_color = chatbot_cfg['branding'].get('primary_color')
        dashboard_color = dashboard_cfg['appearance']['theme'].get('primary')

        if chatbot_color != dashboard_color:
            warnings.append(
                f"Couleurs différentes: Chatbot={chatbot_color}, Dashboard={dashboard_color}"
            )

    return warnings


def main():
    """Point d'entrée principal"""
    print_header("🔍 VALIDATION DES CONFIGURATIONS SAV BOT")

    # Chemins des fichiers
    config_dir = Path(__file__).parent
    chatbot_config_path = config_dir / "chatbot_config.yaml"
    dashboard_config_path = config_dir / "dashboard_config.yaml"

    all_valid = True

    # ── Validation chatbot_config.yaml ──
    print_header("📝 Validation: chatbot_config.yaml")
    chatbot_cfg = load_yaml(chatbot_config_path)

    if chatbot_cfg is None:
        print_error("Impossible de charger chatbot_config.yaml")
        all_valid = False
    else:
        print_success("Fichier chargé avec succès")
        errors = validate_chatbot_config(chatbot_cfg)

        if errors:
            print_error(f"{len(errors)} erreur(s) trouvée(s):")
            for error in errors:
                print(f"  - {error}")
            all_valid = False
        else:
            print_success("Configuration chatbot valide ✨")

    # ── Validation dashboard_config.yaml ──
    print_header("📊 Validation: dashboard_config.yaml")
    dashboard_cfg = load_yaml(dashboard_config_path)

    if dashboard_cfg is None:
        print_error("Impossible de charger dashboard_config.yaml")
        all_valid = False
    else:
        print_success("Fichier chargé avec succès")
        errors = validate_dashboard_config(dashboard_cfg)

        if errors:
            print_error(f"{len(errors)} erreur(s) trouvée(s):")
            for error in errors:
                print(f"  - {error}")
            all_valid = False
        else:
            print_success("Configuration dashboard valide ✨")

    # ── Vérifications croisées ──
    if chatbot_cfg and dashboard_cfg:
        print_header("🔗 Vérifications croisées")
        warnings = check_config_completeness(chatbot_cfg, dashboard_cfg)

        if warnings:
            for warning in warnings:
                print_warning(warning)
        else:
            print_success("Cohérence entre les configurations OK")

    # ── Résumé final ──
    print_header("📋 RÉSUMÉ")

    if all_valid:
        print_success(f"{Colors.BOLD}Toutes les configurations sont valides ! 🎉{Colors.RESET}")
        print_info("Vous pouvez appliquer les changements avec:")
        print_info("  docker-compose restart")
        return 0
    else:
        print_error(f"{Colors.BOLD}Des erreurs ont été détectées ❌{Colors.RESET}")
        print_info("Corrigez les erreurs ci-dessus avant de redémarrer les services")
        return 1


if __name__ == "__main__":
    sys.exit(main())
