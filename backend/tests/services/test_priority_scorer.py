"""
Tests for Priority Scorer service
"""
import pytest
from app.services.priority_scorer import PriorityScorer


class TestPriorityScorer:
    """Test priority scoring functionality"""

    @pytest.fixture
    def scorer(self):
        """Create PriorityScorer instance"""
        return PriorityScorer()

    def test_critical_priority_product_unusable(self, scorer):
        """Test critical priority for unusable product"""
        result = scorer.calculate_priority(
            problem_category="structural",
            problem_severity="P0",
            days_since_purchase=5,
            under_warranty=True,
            has_critical_keywords=True,
        )

        assert result.priority == "P0"

    def test_high_priority_visible_defect(self, scorer):
        """Test high priority for visible defect"""
        result = scorer.calculate_priority(
            problem_category="fabric",
            problem_severity="P1",
            days_since_purchase=10,
            under_warranty=True,
        )

        assert result.priority == "P1"

    def test_medium_priority_minor_issue(self, scorer):
        """Test medium priority for minor aesthetic issue"""
        result = scorer.calculate_priority(
            problem_category="fabric",
            problem_severity="P2",
            days_since_purchase=100,
            under_warranty=True,
        )

        assert result.priority == "P2"

    def test_low_priority_information_request(self, scorer):
        """Test low priority for general information"""
        result = scorer.calculate_priority(
            problem_category="smell",
            problem_severity="P3",
            days_since_purchase=200,
            under_warranty=False,
        )

        # Score: smell(8) + P3(5) + 200j(10) + garantie(5) + première_récl(10) + valeur(2) = 40 → P2
        assert result.priority == "P2"

    def test_priority_increases_with_urgency(self, scorer):
        """Test that critical keywords increase priority"""
        base_result = scorer.calculate_priority(
            problem_category="mechanism",
            problem_severity="P2",
            days_since_purchase=30,
            under_warranty=True,
            has_critical_keywords=False,
        )

        urgent_result = scorer.calculate_priority(
            problem_category="mechanism",
            problem_severity="P2",
            days_since_purchase=30,
            under_warranty=True,
            has_critical_keywords=True,
        )

        assert urgent_result.total_score > base_result.total_score

    def test_warranty_affects_priority(self, scorer):
        """Test that warranty status affects priority"""
        with_warranty = scorer.calculate_priority(
            problem_category="mechanism",
            problem_severity="P2",
            days_since_purchase=30,
            under_warranty=True,
        )

        without_warranty = scorer.calculate_priority(
            problem_category="mechanism",
            problem_severity="P2",
            days_since_purchase=30,
            under_warranty=False,
        )

        assert with_warranty.total_score >= without_warranty.total_score

    def test_newer_products_get_higher_priority(self, scorer):
        """Test that newer products get higher priority"""
        new_product = scorer.calculate_priority(
            problem_category="mechanism",
            problem_severity="P2",
            days_since_purchase=5,
            under_warranty=True,
        )

        old_product = scorer.calculate_priority(
            problem_category="mechanism",
            problem_severity="P2",
            days_since_purchase=200,
            under_warranty=True,
        )

        assert new_product.total_score > old_product.total_score
