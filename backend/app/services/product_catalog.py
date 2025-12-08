# backend/app/services/product_catalog.py
"""
Product Catalog Service
Gère le catalogue produits et recherche d'informations
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ProductCatalog:
    """Service de gestion du catalogue produits"""

    def __init__(self, catalog_path: str = None):
        """
        Initialise le catalogue

        Args:
            catalog_path: Chemin vers le fichier JSON du catalogue
        """
        self.catalog_path = catalog_path or Path(__file__).parent.parent.parent / "data" / "catalog.json"
        self.catalog = self._load_catalog()
        logger.info(f"✅ Catalogue chargé: {len(self.get_all_products())} produits")

    def _load_catalog(self) -> Dict:
        """Charge le catalogue depuis le fichier JSON"""
        try:
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Catalogue non trouvé: {self.catalog_path}, utilisation catalogue vide")
            return {"categories": {}}
        except Exception as e:
            logger.error(f"Erreur chargement catalogue: {e}")
            return {"categories": {}}

    def get_all_products(self) -> List[Dict]:
        """Retourne tous les produits du catalogue"""
        products = []
        for category in self.catalog.get("categories", {}).values():
            products.extend(category.get("products", []))
        return products

    def search_product(self, query: str) -> List[Dict]:
        """
        Recherche un produit par mot-clé

        Args:
            query: Terme de recherche

        Returns:
            Liste de produits correspondants
        """
        query_lower = query.lower()
        results = []

        for product in self.get_all_products():
            # Recherche dans nom, catégorie, ID
            if (query_lower in product.get("name", "").lower() or
                query_lower in product.get("category", "").lower() or
                query_lower in product.get("id", "").lower()):
                results.append(product)

        logger.info(f"🔍 Recherche '{query}': {len(results)} résultats")
        return results

    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """
        Récupère un produit par son ID

        Args:
            product_id: ID du produit (ex: SAL-CAP-001)

        Returns:
            Produit ou None si non trouvé
        """
        for product in self.get_all_products():
            if product.get("id") == product_id:
                return product
        return None

    def get_products_by_category(self, category: str) -> List[Dict]:
        """
        Récupère tous les produits d'une catégorie

        Args:
            category: Nom de la catégorie (salon, salle_a_manger, chambre, decoration)

        Returns:
            Liste de produits
        """
        category_data = self.catalog.get("categories", {}).get(category, {})
        return category_data.get("products", [])

    def get_product_info(self, product_name: str) -> Optional[Dict]:
        """
        Récupère les informations d'un produit par son nom

        Args:
            product_name: Nom du produit

        Returns:
            Informations complètes du produit
        """
        for product in self.get_all_products():
            if product_name.lower() in product.get("name", "").lower():
                return product
        return None

    def get_maintenance_info(self, product_id: str) -> Optional[Dict]:
        """
        Récupère les infos d'entretien d'un produit

        Args:
            product_id: ID du produit

        Returns:
            Infos d'entretien ou None
        """
        product = self.get_product_by_id(product_id)
        if product:
            return product.get("maintenance", {})
        return None

    def get_common_issues(self, product_id: str) -> List[str]:
        """
        Récupère les problèmes courants d'un produit

        Args:
            product_id: ID du produit

        Returns:
            Liste de problèmes courants
        """
        product = self.get_product_by_id(product_id)
        if product:
            return product.get("common_issues", [])
        return []

    def get_warranty_info(self, product_id: str = None) -> Dict:
        """
        Récupère les infos de garantie

        Args:
            product_id: ID du produit (optionnel, retourne info générale si non fourni)

        Returns:
            Infos de garantie
        """
        if product_id:
            product = self.get_product_by_id(product_id)
            if product:
                return {
                    "product_warranty": product.get("warranty", "Non spécifié"),
                    "general_info": self.catalog.get("warranty_info", {})
                }

        return self.catalog.get("warranty_info", {})

    def match_issue_to_product(self, issue_description: str, product_id: str = None) -> Dict:
        """
        Analyse un problème et détermine s'il correspond aux problèmes courants

        Args:
            issue_description: Description du problème
            product_id: ID du produit (optionnel)

        Returns:
            Dict avec match et recommandations
        """
        issue_lower = issue_description.lower()

        # Si produit spécifié
        if product_id:
            product = self.get_product_by_id(product_id)
            if not product:
                return {"match": False, "message": "Produit non trouvé"}

            common_issues = product.get("common_issues", [])
            matched_issues = [
                issue for issue in common_issues
                if any(word in issue_lower for word in issue.lower().split())
            ]

            if matched_issues:
                return {
                    "match": True,
                    "product": product.get("name"),
                    "matched_issues": matched_issues,
                    "warranty": product.get("warranty"),
                    "maintenance": product.get("maintenance", {})
                }

        # Recherche dans tous les produits
        all_matches = []
        for product in self.get_all_products():
            common_issues = product.get("common_issues", [])
            matched = [
                issue for issue in common_issues
                if any(word in issue_lower for word in issue.lower().split())
            ]
            if matched:
                all_matches.append({
                    "product": product.get("name"),
                    "product_id": product.get("id"),
                    "category": product.get("category"),
                    "matched_issues": matched
                })

        return {
            "match": bool(all_matches),
            "possible_products": all_matches[:3]  # Top 3 matchs
        }

    def generate_product_context(self, product_id: str) -> str:
        """
        Génère un contexte formaté pour le chatbot

        Args:
            product_id: ID du produit

        Returns:
            Texte formaté avec toutes les infos produit
        """
        product = self.get_product_by_id(product_id)
        if not product:
            return "Produit non trouvé dans le catalogue."

        context = f"""
📦 PRODUIT: {product.get('name')} ({product.get('id')})
📁 Catégorie: {product.get('category')}
💰 Prix: {product.get('price_range')}€
📏 Dimensions: {product.get('dimensions', {})}
🎨 Matériaux: {', '.join(product.get('materials', []))}
🌈 Couleurs: {', '.join(product.get('colors', []))}

✨ CARACTÉRISTIQUES:
{chr(10).join(['• ' + feat for feat in product.get('features', [])])}

🛡️ GARANTIE: {product.get('warranty')}
🚚 Livraison: {product.get('delivery_time')}

🧹 ENTRETIEN:
{self._format_maintenance(product.get('maintenance', {}))}

⚠️ PROBLÈMES COURANTS:
{chr(10).join(['• ' + issue for issue in product.get('common_issues', [])])}
"""
        return context

    def _format_maintenance(self, maintenance: Dict) -> str:
        """Formate les infos d'entretien"""
        if not maintenance:
            return "Non spécifié"

        lines = []
        for key, value in maintenance.items():
            lines.append(f"• {key.upper()}: {value}")
        return "\n".join(lines)

    def get_categories(self) -> List[str]:
        """Retourne la liste des catégories"""
        return list(self.catalog.get("categories", {}).keys())

    def get_catalog_summary(self) -> Dict:
        """Retourne un résumé du catalogue"""
        categories = {}
        for cat_key, cat_data in self.catalog.get("categories", {}).items():
            products = cat_data.get("products", [])
            categories[cat_key] = {
                "name": cat_data.get("name"),
                "product_count": len(products),
                "products": [p.get("name") for p in products]
            }

        return {
            "total_products": len(self.get_all_products()),
            "categories": categories,
            "version": self.catalog.get("catalog_version", "unknown")
        }

    def get_catalog_summary_for_ai(self) -> str:
        """Génère un résumé du catalogue pour l'IA (compatible avec l'ancien loader)"""
        summary = "CATALOGUE PRODUITS MEUBLE DE FRANCE:\n\n"

        for category_key, category_data in self.catalog.get("categories", {}).items():
            category_name = category_data.get("name", category_key)
            products = category_data.get("products", [])

            summary += f"\n📦 {category_name.upper()}:\n"

            for product in products:
                summary += f"\n- {product.get('name')} ({product.get('id')})\n"
                summary += f"  Prix: {product.get('price_range')}€\n"
                summary += f"  Matériaux: {', '.join(product.get('materials', []))}\n"
                summary += f"  Couleurs: {', '.join(product.get('colors', []))}\n"

                # Dimensions
                dims = product.get('dimensions', {})
                if dims:
                    dim_str = []
                    for key, value in dims.items():
                        if isinstance(value, list):
                            dim_str.append(f"{key}: {', '.join(value)}")
                        else:
                            dim_str.append(f"{key}: {value}")
                    summary += f"  Dimensions: {' | '.join(dim_str)}\n"

                # Features principales
                features = product.get('features', [])
                if features:
                    summary += f"  ✨ {', '.join(features[:3])}\n"

                summary += f"  Délai: {product.get('delivery_time')}\n"
                summary += f"  Garantie: {product.get('warranty')}\n"

        # Info garanties
        warranty = self.catalog.get("warranty_info", {})
        summary += "\n\n🛡️ GARANTIES:\n"
        for key, value in warranty.items():
            if key != 'exclusions':
                summary += f"- {key}: {value}\n"

        return summary


# Instance globale
product_catalog = ProductCatalog()


# Fonction helper pour intégration dans chatbot
def get_product_context_for_chat(product_identifier: str) -> str:
    """
    Récupère le contexte produit pour injection dans le chat

    Args:
        product_identifier: ID ou nom du produit

    Returns:
        Contexte formaté ou message d'erreur
    """
    # Essai par ID
    product = product_catalog.get_product_by_id(product_identifier)

    # Si pas trouvé, essai par nom
    if not product:
        results = product_catalog.search_product(product_identifier)
        if results:
            product = results[0]

    if product:
        return product_catalog.generate_product_context(product.get("id"))
    else:
        return f"⚠️ Produit '{product_identifier}' non trouvé dans notre catalogue."


def search_products_for_issue(issue_description: str) -> str:
    """
    Recherche les produits potentiellement concernés par un problème

    Args:
        issue_description: Description du problème

    Returns:
        Résumé des produits matchés
    """
    result = product_catalog.match_issue_to_product(issue_description)

    if not result.get("match"):
        return "Aucun produit spécifique identifié. Merci de préciser le type de meuble concerné."

    products = result.get("possible_products", [])
    if not products:
        return "Aucun produit correspondant trouvé."

    text = "🔍 Produits potentiellement concernés:\n\n"
    for i, prod in enumerate(products, 1):
        text += f"{i}. **{prod['product']}** ({prod['category']})\n"
        text += f"   Problèmes similaires: {', '.join(prod['matched_issues'][:2])}\n\n"

    text += "Pouvez-vous me confirmer de quel produit il s'agit ?"
    return text
