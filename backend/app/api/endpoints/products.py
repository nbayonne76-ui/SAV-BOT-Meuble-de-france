# backend/app/api/endpoints/products.py
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
import logging
from app.services.product_catalog import product_catalog

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
async def list_products(
    category: Optional[str] = Query(None, description="Filtrer par catégorie (salon, salle_a_manger, chambre, decoration)"),
    search: Optional[str] = Query(None, description="Rechercher des produits"),
    limit: int = Query(50, description="Nombre maximum de résultats")
):
    """
    Liste les produits du catalogue

    - **category**: Filtrer par catégorie (optionnel)
    - **search**: Rechercher par mots-clés (optionnel)
    - **limit**: Limite de résultats (défaut: 50)
    """
    try:
        # Si recherche par mots-clés
        if search:
            products = product_catalog.search_product(search)
            return {
                "success": True,
                "search_query": search,
                "products": products[:limit],
                "total": len(products)
            }

        # Si filtre par catégorie
        if category:
            products = product_catalog.get_products_by_category(category)
            return {
                "success": True,
                "category": category,
                "products": products[:limit],
                "total": len(products)
            }

        # Tous les produits
        products = product_catalog.get_all_products()
        return {
            "success": True,
            "products": products[:limit],
            "total": len(products)
        }

    except Exception as e:
        logger.error(f"List products error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )

@router.get("/categories", status_code=status.HTTP_200_OK)
async def list_categories():
    """Liste toutes les catégories disponibles"""
    try:
        categories = []
        for key, data in product_catalog.catalog.get('categories', {}).items():
            categories.append({
                "id": key,
                "name": data.get('name'),
                "product_count": len(data.get('products', []))
            })

        return {
            "success": True,
            "categories": categories,
            "total": len(categories)
        }
    except Exception as e:
        logger.error(f"List categories error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )

@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product(product_id: str):
    """
    Obtenir les détails d'un produit spécifique

    - **product_id**: ID du produit (ex: SAL-CAP-001)
    """
    try:
        product = product_catalog.get_product_by_id(product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produit {product_id} non trouvé"
            )

        return {
            "success": True,
            "product": product
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get product error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )

@router.get("/catalog/summary", status_code=status.HTTP_200_OK)
async def get_catalog_summary():
    """Obtenir un résumé du catalogue complet"""
    try:
        summary = product_catalog.get_catalog_summary_for_ai()

        return {
            "success": True,
            "catalog_version": product_catalog.catalog.get('catalog_version'),
            "last_updated": product_catalog.catalog.get('last_updated'),
            "summary": summary,
            "total_products": len(product_catalog.get_all_products())
        }
    except Exception as e:
        logger.error(f"Get catalog summary error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )
