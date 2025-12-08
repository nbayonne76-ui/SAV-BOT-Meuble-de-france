#!/usr/bin/env python3
"""
Script de scraping du site Meuble de France
Récupère les produits réels depuis mobilierdefrance.com
"""

import json
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
import time
from pathlib import Path

class MobilierFranceScraper:
    """Scraper pour le site Meuble de France"""

    def __init__(self):
        self.base_url = "https://www.mobilierdefrance.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.products = []

    def scrape_canapes_angle(self) -> List[Dict]:
        """Scrape la page des canapés d'angle"""
        url = f"{self.base_url}/canapes-d-angle"

        print(f"🔍 Scraping: {url}")

        try:
            response = httpx.get(url, headers=self.headers, timeout=30.0, follow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Trouver tous les produits sur la page
            # NOTE: Ces sélecteurs CSS doivent être adaptés selon la structure HTML réelle
            products_found = []

            # Essayer plusieurs sélecteurs possibles
            product_selectors = [
                '.product-item',
                '.product-card',
                '.product',
                '[data-product]',
                '.item-product'
            ]

            product_elements = []
            for selector in product_selectors:
                elements = soup.select(selector)
                if elements:
                    product_elements = elements
                    print(f"✅ Trouvé {len(elements)} produits avec sélecteur: {selector}")
                    break

            if not product_elements:
                print("⚠️  Aucun produit trouvé avec les sélecteurs standards")
                print("🔧 Analyse de la structure HTML pour identification manuelle...")

                # Sauvegarder le HTML pour analyse manuelle
                html_file = Path(__file__).parent / "mobilierdefrance_html.txt"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(soup.prettify())
                print(f"📄 HTML sauvegardé dans: {html_file}")

                return []

            # Extraire les données de chaque produit
            for i, element in enumerate(product_elements, 1):
                try:
                    product = self._extract_product_data(element)
                    if product:
                        products_found.append(product)
                        print(f"  [{i}/{len(product_elements)}] ✅ {product['name']}")
                except Exception as e:
                    print(f"  [{i}/{len(product_elements)}] ❌ Erreur: {e}")

                # Pause pour ne pas surcharger le serveur
                if i % 10 == 0:
                    time.sleep(0.5)

            print(f"\n✅ Total extrait: {len(products_found)} produits")
            return products_found

        except httpx.HTTPError as e:
            print(f"❌ Erreur HTTP: {e}")
            return []
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return []

    def _extract_product_data(self, element) -> Dict:
        """Extrait les données d'un élément produit"""

        # Chercher le nom du produit
        name_selectors = ['.product-name', '.title', 'h2', 'h3', '[itemprop="name"]']
        name = None
        for selector in name_selectors:
            name_elem = element.select_one(selector)
            if name_elem:
                name = name_elem.get_text(strip=True)
                break

        # Chercher le prix
        price_selectors = ['.price', '.product-price', '[itemprop="price"]', '.amount']
        price = None
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price = price_elem.get_text(strip=True)
                break

        # Chercher le lien
        link_elem = element.select_one('a')
        link = None
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            link = href if href.startswith('http') else f"{self.base_url}{href}"

        # Chercher l'image
        img_elem = element.select_one('img')
        image = None
        if img_elem:
            image = img_elem.get('src') or img_elem.get('data-src')

        # Chercher la référence (SKU)
        ref_elem = element.select_one('[data-sku]') or element.select_one('.sku')
        reference = ref_elem.get('data-sku') if ref_elem else None

        if name:
            return {
                "name": name,
                "price": price or "Prix sur demande",
                "link": link,
                "image": image,
                "reference": reference,
                "category": "Canapés d'angle"
            }

        return None

    def generate_catalog_json(self, products: List[Dict], output_file: str):
        """Génère le fichier catalog.json"""

        catalog = {
            "catalog_version": "2.0.0",
            "last_updated": time.strftime("%Y-%m-%d"),
            "source": "mobilierdefrance.com",
            "categories": {
                "salon": {
                    "name": "Salon",
                    "products": []
                }
            }
        }

        # Convertir les produits scrapés au format du catalogue
        for product in products:
            catalog_product = {
                "id": product.get('reference', f"MDF-{hash(product['name']) % 10000}"),
                "name": product['name'],
                "category": "Canapés d'angle",
                "price_range": product['price'],
                "link": product.get('link'),
                "image": product.get('image'),
                "materials": ["Selon modèle"],
                "colors": ["Selon modèle"],
                "dimensions": {
                    "note": "Voir fiche produit sur le site"
                },
                "features": [
                    "Voir détails sur mobilierdefrance.com"
                ],
                "warranty": "2 ans",
                "delivery_time": "Voir fiche produit",
                "maintenance": {
                    "info": "Consultez la fiche produit pour les détails d'entretien"
                },
                "common_issues": []
            }

            catalog["categories"]["salon"]["products"].append(catalog_product)

        # Sauvegarder le catalogue
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Catalogue sauvegardé: {output_path}")
        print(f"📊 Total produits: {len(products)}")

    def run(self):
        """Lance le scraping complet"""
        print("=" * 60)
        print("🚀 SCRAPING MEUBLE DE FRANCE")
        print("=" * 60)
        print()

        # Scraper les canapés d'angle
        products = self.scrape_canapes_angle()

        if products:
            # Générer le catalogue
            output_file = Path(__file__).parent.parent / "backend" / "data" / "catalog.json"
            self.generate_catalog_json(products, str(output_file))

            print()
            print("=" * 60)
            print("✅ SCRAPING TERMINÉ")
            print("=" * 60)
        else:
            print()
            print("=" * 60)
            print("⚠️  SCRAPING INCOMPLET")
            print("=" * 60)
            print()
            print("💡 PROCHAINES ÉTAPES:")
            print("1. Consultez le fichier mobilierdefrance_html.txt")
            print("2. Identifiez les sélecteurs CSS corrects")
            print("3. Mettez à jour la méthode _extract_product_data()")


if __name__ == "__main__":
    scraper = MobilierFranceScraper()
    scraper.run()
