# backend/app/api/endpoints/faq.py
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional
import logging
from app.services.sav_knowledge import sav_kb

logger = logging.getLogger(__name__)
router = APIRouter()


class FAQQuestionResponse(BaseModel):
    id: str
    question: str
    answer: str
    category: str
    category_icon: str
    keywords: List[str]
    popularity: int
    helpful_count: int
    not_helpful_count: int


class FAQCategoryResponse(BaseModel):
    id: str
    name: str
    icon: str
    question_count: int


class FAQVoteRequest(BaseModel):
    question_id: str
    helpful: bool


class AddFAQQuestionRequest(BaseModel):
    category_id: str
    question: str
    answer: str
    keywords: List[str]


@router.get("/", response_model=List[FAQQuestionResponse])
async def search_faq(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category ID")
):
    """
    Search FAQ or get all questions
    """
    try:
        if query:
            # Search FAQ
            results = sav_kb.search_faq(query, category)
        else:
            # Get all from category or all
            if category:
                questions = sav_kb.get_faq_by_category(category)
                # Add category info to each question
                categories = sav_kb.get_all_faq_categories()
                cat_info = next((c for c in categories if c["id"] == category), {})
                results = [
                    {
                        **q,
                        "category": cat_info.get("name", ""),
                        "category_icon": cat_info.get("icon", ""),
                        "relevance_score": 0
                    }
                    for q in questions
                ]
            else:
                # Get all questions from all categories
                results = []
                categories = sav_kb.faq.get("faq", {}).get("categories", [])
                for cat in categories:
                    for q in cat.get("questions", []):
                        results.append({
                            **q,
                            "category": cat.get("name"),
                            "category_icon": cat.get("icon"),
                            "relevance_score": 0
                        })

        logger.info(f"FAQ search: query='{query}', category='{category}', results={len(results)}")

        return results

    except Exception as e:
        logger.error(f"Error searching FAQ: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching FAQ: {str(e)}"
        )


@router.get("/categories", response_model=List[FAQCategoryResponse])
async def get_faq_categories():
    """
    Get list of all FAQ categories
    """
    try:
        categories = sav_kb.get_all_faq_categories()
        logger.info(f"FAQ categories retrieved: {len(categories)}")
        return categories

    except Exception as e:
        logger.error(f"Error getting FAQ categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting categories: {str(e)}"
        )


@router.get("/category/{category_id}", response_model=List[FAQQuestionResponse])
async def get_faq_by_category(category_id: str):
    """
    Get all FAQ questions for a specific category
    """
    try:
        questions = sav_kb.get_faq_by_category(category_id)

        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category_id}' not found"
            )

        # Add category info
        categories = sav_kb.get_all_faq_categories()
        cat_info = next((c for c in categories if c["id"] == category_id), {})

        results = [
            {
                **q,
                "category": cat_info.get("name", ""),
                "category_icon": cat_info.get("icon", "")
            }
            for q in questions
        ]

        logger.info(f"FAQ for category '{category_id}': {len(results)} questions")

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting FAQ by category: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.post("/vote", status_code=status.HTTP_200_OK)
async def vote_faq(vote: FAQVoteRequest):
    """
    Vote on FAQ question helpfulness
    """
    try:
        success = sav_kb.update_faq_stats(vote.question_id, vote.helpful)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question '{vote.question_id}' not found"
            )

        logger.info(f"FAQ vote: question={vote.question_id}, helpful={vote.helpful}")

        return {
            "success": True,
            "message": "Vote recorded",
            "question_id": vote.question_id,
            "helpful": vote.helpful
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording FAQ vote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_faq_question(question: AddFAQQuestionRequest):
    """
    Add a new FAQ question (admin only in production)
    """
    try:
        success = sav_kb.add_faq_question(
            category_id=question.category_id,
            question=question.question,
            answer=question.answer,
            keywords=question.keywords
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{question.category_id}' not found"
            )

        logger.info(f"FAQ question added: category={question.category_id}")

        # Reload knowledge base
        sav_kb.load_knowledge()

        return {
            "success": True,
            "message": "FAQ question added successfully",
            "category_id": question.category_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding FAQ question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_faq_stats():
    """
    Get FAQ statistics
    """
    try:
        stats = sav_kb.faq.get("statistics", {})
        metadata = sav_kb.faq.get("faq", {}).get("metadata", {})

        response = {
            "metadata": metadata,
            "statistics": stats,
            "total_categories": len(sav_kb.get_all_faq_categories())
        }

        logger.info("FAQ stats retrieved")

        return response

    except Exception as e:
        logger.error(f"Error getting FAQ stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )
