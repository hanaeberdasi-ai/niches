"""
Tests for scoring systems
"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scoring.niche_score import NicheScorer, value_to_level, ScoreLevel
from scoring.store_score import StoreScorer


class TestNicheScoring:
    """Tests for niche scoring"""
    
    def test_value_to_level(self):
        """Test score level conversion"""
        assert value_to_level(85) == ScoreLevel.VERY_HIGH
        assert value_to_level(70) == ScoreLevel.HIGH
        assert value_to_level(50) == ScoreLevel.MEDIUM
        assert value_to_level(25) == ScoreLevel.LOW
        assert value_to_level(10) == ScoreLevel.VERY_LOW
    
    def test_basic_scoring(self):
        """Test basic niche scoring"""
        scorer = NicheScorer()
        
        score = scorer.calculate_score(
            niche_name="Test Niche",
            category="Test Category",
            subcategory="Test Subcategory",
            stores_found=10,
            products_found=50,
            avg_price=50.0,
        )
        
        # Score should be between 0 and 100
        assert 0 <= score.overall_score <= 100
        
        # Should have all components
        assert "demand" in score.components
        assert "trend" in score.components
        assert "competition" in score.components
        assert "product_opportunity" in score.components
    
    def test_high_opportunity_scoring(self):
        """Test scoring for high opportunity niche"""
        scorer = NicheScorer()
        
        score = scorer.calculate_score(
            niche_name="High Opportunity",
            category="Electronics",
            subcategory="Gadgets",
            stores_found=15,
            products_found=100,
            avg_price=100.0,
            gmc_suitability="suitable",
        )
        
        # Should have relatively high score
        assert score.overall_score >= 50
        assert len(score.strengths) > 0
    
    def test_low_opportunity_scoring(self):
        """Test scoring for low opportunity niche"""
        scorer = NicheScorer()
        
        score = scorer.calculate_score(
            niche_name="Low Opportunity",
            category="Unknown",
            subcategory="Unknown",
            stores_found=50,  # High competition
            products_found=5,  # Low product variety
            avg_price=5.0,    # Low price
            gmc_suitability="high_risk",
        )
        
        # Should have lower score
        assert score.overall_score < 70
        assert len(score.weaknesses) > 0


class TestStoreScoring:
    """Tests for store scoring"""
    
    def test_basic_store_scoring(self):
        """Test basic store scoring"""
        scorer = StoreScorer()
        
        store_info = {
            "name": "Test Store",
            "domain": "teststore.com",
            "description": "A test store",
            "currency": "USD",
            "social_links": {"instagram": "https://instagram.com/test"},
            "detected_apps": ["Klaviyo", "Yotpo"],
            "theme": "Dawn",
        }
        
        products = [
            {"title": "Product 1", "price": 50.0, "product_type": "Type A"},
            {"title": "Product 2", "price": 75.0, "product_type": "Type B"},
            {"title": "Product 3", "price": 100.0, "product_type": "Type A"},
        ]
        
        score = scorer.calculate_score(
            store_info=store_info,
            products=products,
            target_niche="test",
        )
        
        # Score should be between 0 and 100
        assert 0 <= score.overall_score <= 100
        
        # Should have components
        assert "catalog_depth" in score.components
        assert "pricing" in score.components
        assert "technology" in score.components
    
    def test_empty_store_scoring(self):
        """Test scoring with minimal store info"""
        scorer = StoreScorer()
        
        score = scorer.calculate_score(
            store_info={},
            products=[],
        )
        
        # Should still return a valid score
        assert 0 <= score.overall_score <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
