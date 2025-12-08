# backend/app/services/catalog_loader.py
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class CatalogLoader:
    """Chargeur de catalogue produits"""

    def __init__(self, catalog_path: str = "data/catalog.json"):
        self.catalog_path = Path(catalog_path)
        self.catalog = None
        self.load_catalog()

    def load_catalog(self):
        """Charge le catalogue depuis le fichier JSON"""
        try:
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                self.catalog = json.load(f)
            logger.info(f"Catalogue chargé: {self.catalog['catalog_version']}")
        except Exception as e:
            logger.error(f"Erreur chargement catalogue: {str(e)}")
            self.catalog = {"categories": {}}

    def get_all_products(self) -> List[Dict]:
        """Retourne tous les produits de toutes les catégories"""
        products = []
        for category_key, category_data in self.catalog.get('categories', {}).items():
            products.extend(category_data.get('products', []))
        return products

    def get_products_by_category(self, category: str) -> List[Dict]:
        """Retourne les produits d'une catégorie"""
        category_data = self.catalog.get('categories', {}).get(category, {})
        return category_data.get('products', [])

    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Trouve un produit par son ID"""
        for product in self.get_all_products():
            if product.get('id') == product_id:
                return product
        return None

    def search_products(self, query: str) -> List[Dict]:
        """Recherche des produits par mots-clés"""
        query_lower = query.lower()
        results = []

        for product in self.get_all_products():
            # Recherche dans le nom
            if query_lower in product.get('name', '').lower():
                results.append(product)
                continue

            # Recherche dans la catégorie
            if query_lower in product.get('category', '').lower():
                results.append(product)
                continue

            # Recherche dans les features
            features_str = ' '.join(product.get('features', [])).lower()
            if query_lower in features_str:
                results.append(product)

        return results

    def get_catalog_summary_for_ai(self) -> str:
        """Génère un résumé du catalogue pour l'IA"""
        summary = "CATALOGUE PRODUITS MEUBLE DE FRANCE:\n\n"

        for category_key, category_data in self.catalog.get('categories', {}).items():
            category_name = category_data.get('name', category_key)
            products = category_data.get('products', [])

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
        warranty = self.catalog.get('warranty_info', {})
        summary += "\n\n🛡️ GARANTIES:\n"
        for key, value in warranty.items():
            if key != 'exclusions':
                summary += f"- {key}: {value}\n"

        return summary

# Instance globale
catalog_loader = CatalogLoader()
